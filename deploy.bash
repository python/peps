#!/bin/bash
set -ex
make package
pip install awscli
aws s3 cp --acl public-read build/peps.tar.gz s3://pythondotorg-assets-staging/peps.tar.gz
aws s3 cp --acl public-read build/peps.tar.gz s3://pythondotorg-assets/peps.tar.gz
