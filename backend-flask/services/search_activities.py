from datetime import datetime, timedelta, timezone

#honeycomb
from opentelemetry import trace

tracer = trace.get_tracer("search.activities")

class SearchActivities:
  def run(search_term):
    with tracer.start_as_current_span("http-search-activities"):
      span = trace.get_current_span()
      now = datetime.now(timezone.utc).astimezone()
      span.set_attribute("app.now", now.isoformat())
      # In the future this 'attribute' is going to be dynamic data from DB
      span.set_attribute("search.term", search_term)

      model = {
        'errors': None,
        'data': None
      }

      now = datetime.now(timezone.utc).astimezone()

      if search_term == None or len(search_term) < 1:
        model['errors'] = ['search_term_blank']
      else:
        results = [{
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Andrew Brown',
          'message': 'Cloud is fun!',
          'created_at': now.isoformat()
        }]
        model['data'] = results
        span.set_attribute("search.result_length", len(results))
      return model