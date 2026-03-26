# AWS Support

Use this reference when the user asks for AWS-native diagrams or wants AWS resources mixed into a draw.io architecture.

## Generated Assets

Run:

```bash
cd <skill-directory>/skills/oci-drawio
bash setup.sh --provider aws
```

This generates:

- `icons/aws-shapes.xml`
- `components/aws_components.json`
- `components/aws/index.json`
- `components/aws/{category}.json`

## Loading Pattern

1. Read `components/aws/index.json` to identify the category for a needed AWS resource.
2. Read only the relevant category file under `components/aws/`.
3. Copy the `style` string as-is into the `.drawio` XML.

Example:

```python
import json

with open("components/aws/networking.json") as f:
    networking = json.load(f)

alb_style = networking["Elastic Load Balancing"]["style"]
api_gw_style = networking["Amazon API Gateway"]["style"]
```

## Typical AWS Categories

| Category file | Examples |
|---------------|----------|
| `components/aws/networking.json` | VPC, Public Subnet, Private Subnet, Elastic Load Balancing, Amazon API Gateway, AWS Transit Gateway |
| `components/aws/compute.json` | Amazon EC2, AWS Lambda, AWS Batch, AWS App Runner |
| `components/aws/container.json` | Amazon Elastic Container Service, Amazon Elastic Kubernetes Service, AWS Fargate |
| `components/aws/database.json` | Amazon RDS, Amazon Aurora, Amazon DynamoDB |
| `components/aws/storage.json` | Amazon S3, Amazon EBS, Amazon EFS |
| `components/aws/security.json` | AWS IAM, AWS KMS, AWS WAF |

## Layout Guidance

- Use `Region` as the outer container.
- Put `VPC` inside the Region.
- Put `Public Subnet` and `Private Subnet` inside the VPC.
- Keep internet-facing resources such as `Elastic Load Balancing` or `Amazon API Gateway` in the public tier.
- Keep app compute and data stores in private tiers unless the user explicitly wants a public data service.
- Managed regional services such as `Amazon S3` can be shown outside the VPC but inside the Region.

## Container Styles

These simple container styles work well with AWS icons:

### Region

```
rounded=1;whiteSpace=wrap;html=1;arcSize=0;strokeColor=#545B64;fillColor=#FFFFFF;dashed=0;verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;fontSize=14;fontColor=#000000;
```

### VPC

```
rounded=1;whiteSpace=wrap;html=1;arcSize=0;strokeColor=#FF9900;fillColor=none;dashed=1;dashPattern=8 4;verticalAlign=top;align=left;spacingLeft=10;fontStyle=1;fontSize=12;fontColor=#FF9900;
```

### Subnet

```
rounded=1;whiteSpace=wrap;html=1;arcSize=0;strokeColor=#FF9900;fillColor=none;dashed=1;dashPattern=8 4;verticalAlign=top;align=left;spacingLeft=10;fontSize=11;fontColor=#FF9900;
```

## Useful IDs

Use descriptive IDs such as `region-1`, `vpc-1`, `subnet-public-1`, `subnet-private-1`, `alb-1`, `api-gw-1`, `ecs-1`, `lambda-1`, `rds-1`, `s3-1`, `tgw-1`.
