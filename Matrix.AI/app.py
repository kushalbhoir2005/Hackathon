from flask import Flask, render_template, jsonify, request
from eda import get_dashboard_data
from langchain_bot import generate_langchain_insights, chat_with_data
import pandas as pd

app = Flask(__name__)

# =========================
# GLOBAL STORE
# =========================
uploaded_data_store = {}

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")

# =========================
# DASHBOARD API
# =========================
@app.route("/api/data")
def data():
    data = get_dashboard_data()

    try:
        insights = generate_langchain_insights(data)

        if not isinstance(insights, list) or len(insights) == 0:
            raise ValueError("Invalid AI output")

    except Exception as e:
        print("AI ERROR:", e)
        insights = [{
            "type": "info",
            "title": "AI unavailable",
            "body": "Showing fallback insights."
        }]

    data["recommendations"] = insights

    return jsonify(data)

# =========================
# CHATBOT
# =========================
@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message", "")

        if not user_message:
            return jsonify({"reply": "Please ask a question!"})

        # Use uploaded or default data
        data_context = uploaded_data_store if uploaded_data_store else get_dashboard_data()

        # Force factual answers for KPIs
        if "loss" in user_message.lower():
            ai_reply = f"Total loss (lost revenue) is {data_context['kpis']['lost_revenue']}"

        elif "profit" in user_message.lower():
            ai_reply = f"Estimated profit is {data_context['kpis']['profit']}"

        else:
            ai_reply = chat_with_data(user_message, data_context)

        return jsonify({"reply": ai_reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})
# =========================
# FILE UPLOAD
# =========================
@app.route("/api/upload", methods=["POST"])
def upload():
    global uploaded_data_store

    try:
        file = request.files["file"]
        df = pd.read_csv(file)

        # KPIs
        kpis = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": int(df.isnull().sum().sum())
        }

        # Chart (first numeric column)
        numeric_cols = df.select_dtypes(include=['int64','float64']).columns.tolist()

        chart_data = {}
        if numeric_cols:
            col = numeric_cols[0]
            chart_data = {
                "labels": list(range(len(df.head(20)))),
                "values": df[col].head(20).tolist(),
                "column": col
            }

        # AI insights (use structured summary, NOT raw rows)
        try:
            summary_data = {
                "kpis": kpis,
                "sample_columns": list(df.columns)
            }

            insights = generate_langchain_insights(summary_data)

            if not isinstance(insights, list) or len(insights) == 0:
                raise ValueError("Bad AI output")

        except Exception as ai_error:
            print("AI ERROR:", ai_error)
            insights = [{
                "type": "info",
                "title": "AI unavailable",
                "body": "Basic dataset summary shown."
            }]

        uploaded_data_store = {
            "kpis": kpis,
            "chart": chart_data,
            "recommendations": insights
        }

        return jsonify({"status": "success"})

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return jsonify({"status": "error", "message": str(e)})

# =========================
# PAGES
# =========================
@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

@app.route("/api/analysis-data")
def analysis_data():
    return jsonify(uploaded_data_store)

@app.route("/walmart-insights")
def walmart_insights():
    return render_template("walmart.html")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)