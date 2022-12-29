# Notes on Cloudformation

TODO:

- Add throdelling for SearchAPI stack? There's an account limit already in place.
- Add label, that stops CF from being deleted if PR is closed? That way, you can close/open a PR to refresh it, and not have to wait for the stack.
- Do I need to enable CORS for the API?
- Add WAF to cloudfront directly, or just API?
- Cloudfront cache disabled on old distro. Is that what we want?
- Same Tag lockdown I did to cloudfront, do to apigateway

Notes from Andrew's meetup:

- Trying out ProvisionedConcurrency. Might also help with AWS random resets, that a keep-worm cloudwatch can still hit. Use 8-10 for prod.
