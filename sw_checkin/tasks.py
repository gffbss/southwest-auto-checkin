from datetime import datetime
from celery.task import task
from sw_checkin.checkin import *
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@task(ignore_result=False, default_retry_delay=10, max_retries=20)
def checkin_job(reservation):
    logger.info("Attempting checkin for " + reservation.__str__())
    logger.info('Retry: ' + str(checkin_job.request.retries))
    checkin = CheckIn(reservation.confirmation_num, reservation.passenger.first_name, reservation.passenger.last_name, reservation.passenger.email)
    # todo: save only content for success and parse out boarding pass
    response_code, content = checkin.post_to_sw()
    filename = './res' + str(reservation.id) + '_' + str(checkin_job.request.retries) + '_content.html'
    print >> open(filename, 'w+'), content.replace("/assets", "http://southwest.com/assets")
    if response_code == RESPONSE_STATUS_SUCCESS.code:
        logger.info("Successfully checked in for reservation: " + reservation.__str__())
        logger.info('Time: ' + str(datetime.now().time()))
        logger.info('Reservation time: ' + str(reservation.flight_time))
        # reservation.success = True
        # reservation.save()
        return True
    elif response_code == RESPONSE_STATUS_TOO_EARLY.code:
        logger.info('Time: ' + str(datetime.now().time()))
        logger.info('Reservation time: ' + str(reservation.flight_time))
        checkin_job.retry(args=[reservation])
    elif response_code == RESPONSE_STATUS_INVALID.code:
        logger.error("Invalid reservation, id: " + str(reservation.id))
        return False
    elif response_code == RESPONSE_STATUS_RES_NOT_FOUND.code:
        logger.error("Reservation not found, id: " + str(reservation.id))
        return False
    else:
        logger.error("Unknown error, retrying...")
        checkin_job.retry(args=[reservation])
