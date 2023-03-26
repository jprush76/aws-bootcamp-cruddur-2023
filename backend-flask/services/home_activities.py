from datetime import datetime, timedelta, timezone
from lib.db import db

#honeycomb
from opentelemetry import trace

tracer = trace.get_tracer("home.activities")

class HomeActivities:
  def run(cognito_user_id=None):
  # def run(logger): // for cloudwathc logs
    #logger.info('Hello Cloudwatch! from  /api/activities/home')
    with tracer.start_as_current_span("http-home-activities"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      
      #span.set_attribute("app.result_length", len(results))
      sql = db.template('activities', 'home')
      results = db.query_array_json(sql)
      return results