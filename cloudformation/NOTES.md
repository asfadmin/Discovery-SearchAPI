# Notes on Cloudformation

TODO:

- Add throdelling for SearchAPI stack? There's an account limit already in place.
- Add label, that stops CF from being deleted if PR is closed? That way, you can close/open a PR to refresh it, and not have to wait for the stack.
- Do I need to enable CORS for the API?
- Add WAF to cloudfront directly, or just API?
- Cloudfront cache disabled on old distro. Is that what we want?
- With CloudFront cert, is the ID/Arn private?
- Add DENY for tag/untag resources outside of SearchAPI? https://docs.amazonaws.cn/en_us/AmazonCloudFront/latest/DeveloperGuide/access-control-overview.html
- Same Tag lockdown I did to cloudfront, do to apigateway
- Do we need cloudfront logs, if we have gateway ones?
