import json
import pulumi
import pulumi_aws as aws

# Create a DynamoDB table for storing user and group data
table = aws.dynamodb.Table('userTable',
    attributes=[aws.dynamodb.TableAttributeArgs(name='id', type='S')],
    hash_key='id',
    read_capacity=20,
    write_capacity=20,
)

# Create a role for Lambda functions
role = aws.iam.Role("role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com",
            },
        }],
    }),
    managed_policy_arns=[
        aws.iam.ManagedPolicy.AWS_LAMBDA_BASIC_EXECUTION_ROLE,
        "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    ]
)

# Create Lambda functions for each endpoint
functions = {}
endpoints = [
    'check_messages', 'register', 'send_message', 'check_block', 'block_user',
    'create_group', 'manage_group'
]

for endpoint in endpoints:
    functions[endpoint] = aws.lambda_.Function(endpoint,
        runtime="python3.9",
        handler=f'{endpoint}.lambda_handler',
        role=role.arn,
        code=pulumi.AssetArchive({
            f'{endpoint}.py': pulumi.FileAsset(f'./endpoints/{endpoint}.py'),
            'database.py': pulumi.FileAsset('./database.py')
        })
    )

# Create an API Gateway
api = aws.apigatewayv2.Api("api", protocol_type="HTTP")

# Create integrations and routes for each endpoint sequentially to ensure consistency
for endpoint, function in functions.items():
    integration = aws.apigatewayv2.Integration(endpoint,
        api_id=api.id,
        integration_type="AWS_PROXY",
        integration_uri=function.arn
    )

    permission = aws.lambda_.Permission(f'{endpoint}_permission',
        action="lambda:InvokeFunction",
        function=function.name,
        principal="apigateway.amazonaws.com",
        source_arn=pulumi.Output.concat(api.execution_arn, "/*/*")
    )

    route = aws.apigatewayv2.Route(endpoint,
        api_id=api.id,
        route_key=f"POST /{endpoint}",
        target=integration.id.apply(lambda id: "integrations/" + id)
    )

# Deploy the API
deployment = aws.apigatewayv2.Deployment("api_deployment",
    api_id=api.id,
    opts=pulumi.ResourceOptions(depends_on=list(functions.values()))
)
stage = aws.apigatewayv2.Stage("api_stage",
    api_id=api.id,
    name="v1",
    deployment_id=deployment.id
)

# Export the URL of the deployed API
pulumi.export("url", pulumi.Output.concat(api.api_endpoint, "/", stage.name))