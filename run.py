from app import app
from healthcheck_ep import *
from apscheduler.schedulers.background import BackgroundScheduler

# sched = BackgroundScheduler(job_defaults={'max_instances': 2})
# sched.add_job(func=healthcheck, trigger='interval', seconds=10)
# sched.start()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)