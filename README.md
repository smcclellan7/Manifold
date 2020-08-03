# Manifold Code Test - Name and Zip Service
A simple web service that extracts full name and zip code information from a JSON record and stores it in a database.
The service can be launched using [AWS Cloudformation](https://aws.amazon.com/cloudformation/).

## Overview
The service consists of three components
- **NameAndZipBucket** - an [S3](https://aws.amazon.com/s3/) bucket for storing the extracted info.
- **ExtractAndStore** - a [Lambda](https://aws.amazon.com/lambda/) function that does the work of extracting the info and storing it in the NameAndZipBucket.
- **HttpApi** - an [API Gateway](https://aws.amazon.com/api-gateway/) that exposes the service to the web. All requests to the API are passed directly to the ExtractAndStore function.

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

## HttpApi
The HttpApi is a simple gateway that passes any incoming request to the ExtractAndStore function.
