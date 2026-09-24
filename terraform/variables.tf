variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Elastic Beanstalk application name and ECR repository name."
  type        = string
  default     = "storeops"
}

variable "environment_name" {
  description = "Elastic Beanstalk environment name."
  type        = string
  default     = "storeops-env"
}

variable "instance_type" {
  description = "EC2 instance type for the Beanstalk environment (single instance, Section#6)."
  type        = string
  default     = "t3.micro"
}

variable "solution_stack_name" {
  description = <<-EOT
    Elastic Beanstalk Docker platform solution stack. Beanstalk solution
    stacks are versioned and change over time — verify the current value
    with: aws elasticbeanstalk list-available-solution-stacks --query
    "SolutionStacks[?contains(@,'Docker')]" and update this default.
  EOT
  type        = string
  default     = "64bit Amazon Linux 2023 v4.3.5 running Docker"
}

variable "container_port" {
  description = "Port the app listens on inside the container (must match Dockerrun.aws.json and the Dockerfile's PORT)."
  type        = number
  default     = 8000
}

variable "log_level" {
  description = "Log level passed to the app as an environment variable."
  type        = string
  default     = "info"
}
