from aws_cdk import (core, aws_ec2 as ec2, aws_ecs as ecs, 
                     aws_ecs_patterns as ecs_patterns, aws_rds as rds)


class SonarStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(self, "SonarVpc", max_azs=3)     # default is all AZs in region

        cluster = rds.DatabaseCluster(self, 'Database', 
            engine= rds.DatabaseClusterEngine.AURORA,
            master_user= rds.Login(
                username = 'admin'
            ),
            instance_props= rds.InstanceProps(
               instance_type= ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
                vpc_subnets= ec2.SubnetSelection(
                    subnet_type= ec2.SubnetType.PRIVATE
                ),
                vpc = vpc 
            )
        )

        cluster = ecs.Cluster(self, "SonarCluster", vpc=vpc)

        ecs_patterns.ApplicationLoadBalancedFargateService(self, "SonarService",
            cluster=cluster,            # Required
            cpu=512,                    # Default is 256
            desired_count=6,            # Default is 1
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("sonarqube"),
                container_port=9000
            ),
            memory_limit_mib=2048,      # Default is 512
            public_load_balancer=True)
