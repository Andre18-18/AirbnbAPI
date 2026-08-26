
variable "project_name" {
  type    = string
  default = "andre-tests"
}

variable "instance_type" {
  type    = string
  default = "c7i-flex.large" #t2.micro was not working
}

variable "ami" {
  type    = string
  default = "ami-03446a3af42c5e74e"
}

variable "docker_username" {
  type = string
}

variable "docker_password" {
  type      = string
  sensitive = true
}

variable "docker_repo" {
  type = string
}
