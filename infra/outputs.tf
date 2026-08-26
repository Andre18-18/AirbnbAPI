
output "instance_public_ip" {
  value = aws_instance.api-ec2-instance.public_ip
}

output "instance_public_dns" {
  value = aws_instance.api-ec2-instance.public_dns
}

output "ssh_command" {
  value = "ssh -i ${var.project_name}-key.pem ubuntu@${aws_instance.api-ec2-instance.public_dns}"
}
