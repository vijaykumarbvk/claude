############################
# RDS — MySQL
#
# The app follows database-per-service, but all four logical databases
# live on one RDS instance here to keep cost sane for a dev/demo build.
# Schema isolation is preserved (venus_user_db, venus_doctor_db, ...),
# so splitting them onto separate instances later is a config change,
# not a code change.
############################

resource "aws_db_subnet_group" "venus" {
  name       = "${var.cluster_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private1.id, aws_subnet.private2.id]

  tags = merge(var.project_tags, { Name = "${var.cluster_name}-db-subnet-group" })
}

resource "aws_db_instance" "mysql" {
  identifier     = "${var.cluster_name}-mysql"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = "venus_user_db"
  username = var.db_username
  password = var.db_password
  port     = 3306

  db_subnet_group_name   = aws_db_subnet_group.venus.name
  vpc_security_group_ids = [aws_security_group.data_tier.id]

  # Private only — the pods reach it over the VPC, nothing else can.
  publicly_accessible = false
  multi_az            = false

  backup_retention_period = 7
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = merge(var.project_tags, { Name = "${var.cluster_name}-mysql" })
}
