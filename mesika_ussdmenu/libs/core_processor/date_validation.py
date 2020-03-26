import core_processor
import datetime

logfile = "date_validation"


def validate_date(date):
    try:
        input_date = datetime.datetime.strptime(date, '%Y-%m-%d')
        today = datetime.datetime.now()
        core_processor.libhandler.writelog(logfile, f"Input date: {input_date} & Today is: {today}")

        if input_date < today:
            return True

        else:
            return False

    except ValueError:
        return False
