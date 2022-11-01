# Notes on Cloudformation

TODO:

- Add throdelling for SearchAPI stack? There's an account limit already in place.

Notes from Andrew's meetup:

- Trying out ProvisionedConcurrency. Might also help with AWS random resets, that a keep-worm cloudwatch can still hit. Use 8-10 for prod.
- Instead of API Gateway, use the lambda url directly? Avoids the 30sec gateway timeout.
