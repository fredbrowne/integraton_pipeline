resource "aws_apigatewayv2_api" "http_api" {
  name          = var.api_name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id     = aws_apigatewayv2_api.http_api.id
  name       = "$default"
  auto_deploy = true
}

# Create integrations for each route
resource "aws_apigatewayv2_integration" "lambda_integration" {
  for_each          = var.routes
  api_id            = aws_apigatewayv2_api.http_api.id
  integration_type  = "AWS_PROXY"
  integration_uri   = each.value
  payload_format_version = "2.0"
}

# Create routes for each integration
resource "aws_apigatewayv2_route" "http_route" {
  for_each   = var.routes
  api_id     = aws_apigatewayv2_api.http_api.id
  route_key  = each.key
  target     = "integrations/${aws_apigatewayv2_integration.lambda_integration[each.key].id}"
}
