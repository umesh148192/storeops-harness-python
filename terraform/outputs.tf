output "ecr_repository_url" {
  description = "Push images here (used by the CI/CD pipeline)."
  value       = aws_ecr_repository.app.repository_url
}

output "environment_url" {
  description = "Public URL of the Beanstalk environment."
  value       = "http://${aws_elastic_beanstalk_environment.env.cname}"
}

output "environment_name" {
  value = aws_elastic_beanstalk_environment.env.name
}

output "application_name" {
  value = aws_elastic_beanstalk_application.app.name
}
