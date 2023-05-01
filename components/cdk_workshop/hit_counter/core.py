from constructs import Construct
from aws_cdk import aws_lambda as _lambda, aws_dynamodb as ddb
from aws_cdk import BundlingOptions


class HitCounter(Construct):
    @property
    def handler(self):
        return self._handler

    @property
    def table(self):
        return self._table

    def __init__(
        self, scope: Construct, id: str, downstream: _lambda.IFunction, **kwargs
    ):
        super().__init__(scope, id, **kwargs)

        self._table = ddb.Table(
            self,
            "Hits",
            partition_key={"name": "path", "type": ddb.AttributeType.STRING},
        )

        self._handler = _lambda.Function(
            self,
            "HitCounterHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="cdk_workshop.hitcounter_lambda.core.handler",
            code=_lambda.Code.from_asset(
                "lambda/hitcounter",
                bundling=BundlingOptions(
                    image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t"
                        " /asset-output && cp -au . /asset-output"
                    ]
                )
            ),
            environment={
                "DOWNSTREAM_FUNCTION_NAME": downstream.function_name,
                "HITS_TABLE_NAME": self._table.table_name,
            },
        )

        self._table.grant_read_write_data(self._handler)
        downstream.grant_invoke(self._handler)
