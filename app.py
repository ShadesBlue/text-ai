from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import json
import pyreadstat

from ai import ask_groq
from analysis.statistics import *
from analysis.visualization import generate_analysis_plot

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

df_global = None

# ---------- AI PARSER ----------
def ai_parse_command(user_input, columns):
    prompt = f"""
    Convert this into JSON:
    "{user_input}"

    Columns: {columns}

    Format:
    {{
      "analysis_type": "...",
      "variables": ["..."]
    }}
    """

    response = ask_groq(prompt)

    try:
        parsed = json.loads(response)
        return parsed.get("analysis_type"), {"variables": parsed.get("variables", [])}
    except:
        return None, {}

# ---------- AI EXPLAIN ----------
def explain_results(result_html):
    explanation = ask_groq(f"Explain this statistical result simply:\n{result_html}")
    return explanation or ""

# ---------- ROUTES ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    global df_global
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file uploaded"})

    filename = file.filename.lower()

    try:
        if filename.endswith(".csv"):
            df_global = pd.read_csv(file)
        elif filename.endswith(".xlsx"):
            df_global = pd.read_excel(file)
        elif filename.endswith(".sav"):
            df_global, meta = pyreadstat.read_sav(file)
        elif filename.endswith(".dta"):
            df_global, meta = pyreadstat.read_dta(file)
        else:
            return jsonify({"error": "Unsupported file format"})
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"})

    return jsonify({"columns": df_global.columns.tolist()})

@app.route("/run", methods=["POST"])
def run():
    global df_global

    if df_global is None:
        return jsonify({"error": "Upload dataset first"})

    user_input = request.json.get("command")

    analysis_type, params = ai_parse_command(user_input, df_global.columns.tolist())

    if not analysis_type:
        return jsonify({"error": "Could not understand command"})

    variables = params.get("variables", [])

    # ---------- MAP ANALYSIS ----------
    if analysis_type == "descriptive":
        result, plot = descriptive_stats(df_global, variables)

    elif analysis_type == "correlation":
        result, plot = correlation_analysis(df_global, variables)

    elif analysis_type == "regression":
        if len(variables) >= 2:
            result, plot = linear_regression(df_global, variables[0], variables[1:])
        else:
            return jsonify({"error": "Need dependent + independent variables"})

    elif analysis_type == "anova":
        result, plot = anova_analysis(df_global, variables)

    elif analysis_type == "chi_square":
        result, plot = chi_square_test(df_global, variables)

    elif analysis_type == "logistic_regression":
        result, plot = logistic_regression(df_global, variables)

    else:
        return jsonify({"error": f"{analysis_type} not supported yet"})

    image_url = generate_analysis_plot(plot) if plot else None
    explanation = explain_results(result)

    return jsonify({
        "result": result,
        "plot": image_url,
        "explanation": explanation
    })


if __name__ == "__main__":
    app.run(debug=True)
