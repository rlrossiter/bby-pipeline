import json
import uuid

import azure.functions as func
from scraper_pipeline.models import page_content
from scraper_pipeline.process import state_processor


def main(msg: func.ServiceBusMessage, notification: func.Out[str]):
    json_str = msg.get_body().decode('utf-8')
    content = page_content.PageContent(**json.loads(json_str))

    proc = state_processor.StateProcessor()

    notif = proc.process(content)

    if notif:
        notification.set(json.dumps(notif._asdict()))

    row_key = str(uuid.uuid4())
    table_row = {
        "PartitionKey": content.page_id,
        "RowKey": row_key,
        **content._asdict()
    }

    return json.dumps(table_row)