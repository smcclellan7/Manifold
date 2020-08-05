# Manifold Code Test - Name and Zip Service
A simple web service that extracts full name and zip code information from a JSON record and stores it in a database.
The service can be launched using [AWS Cloudformation](https://aws.amazon.com/cloudformation/).

## Overview
The service consists of three components
- **NameAndZipBucket** - an [S3](https://aws.amazon.com/s3/) bucket for storing the extracted info.
- **ExtractAndStore** - a [Lambda](https://aws.amazon.com/lambda/) function that does the work of extracting the info and storing it in the NameAndZipBucket.
- **ApiGateway** - an [API Gateway](https://aws.amazon.com/api-gateway/) that exposes the service to the web. All requests to the API are passed directly to the ExtractAndStore function.

## NameAndZipBucket
The NameAndZipBucket stores the extracted info as a JSON string. E.g.
``
{
  "first_name": "Steve",
  "middle_name": "Martin",
  "last_name": "McClellan",
  "zip_code": 94806
}
``
Records are keyed with a random UUID.

## ExtractAndStore
ExtractAndStore runs a Python function to find fields named `first_name`, `middle_name`, `last_name`, and `zip_code` anywhere inside the incoming JSON record. These fields are extracted, if they exist, and stored as a new record in the NameAndZipBucket.

## ApiGateway
The ApiGateway is a simple REST API that passes any incoming POST request to the ExtractAndStore function.

## Deployment
The service can be deployed to AWS with the [AWS Command Line Interface](https://docs.aws.amazon.com/cli/) using the following steps:
1. If this is your first time using AWS CLI:
    1. Install the AWS CLI v2 for your operating system: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
    1. Configure your AWS client with `aws configure`
1. You need an S3 bucket for storing code files. If you don't have one already, create one with `aws s3api create-bucket --bucket {bucket-name} --create-bucket-configuration LocationConstraint={region}`
  Note that the namespace for S3 buckets is shared by all users, so you need to pick a unique name.
1. Clone this repository to your computer: `git clone https://github.com/smcclellan7/Manifold.git`
1. From the root directory of the cloned repo, create a packaged template: `aws cloudformation package --template template.yaml --s3-bucket {bucket-name} --output-template-file packaged-template.yaml`
1. Deploy the packaged template: `aws cloudformation deploy --template-file packaged-template.yaml --stack-name name-and-zip --capabilities CAPABILITY_IAM`
1. Once the deployment is complete, the API endpoint will be available at https://{API-gateway-id}.execute-api.{region}.amazonaws.com/Prod. You can also find this link in your AWS Console: https://console.aws.amazon.com/apigateway/
