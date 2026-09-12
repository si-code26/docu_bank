#!/bin/bash

echo "Initializing LocalStack"

awslocal s3 mb s3://docubank-uploads
awslocal sqs create-queue --queue-name docubank-ingest

echo "LocalStack initialized"