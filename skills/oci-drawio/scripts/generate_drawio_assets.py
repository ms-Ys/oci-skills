from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


OCI_CATEGORY_MAP = {
    "compute": "compute",
    "networking": "networking",
    "network": "networking",
    "database": "database",
    "storage": "storage",
    "identitysecurity": "security",
    "identity security": "security",
    "identityandsecurity": "security",
    "identity&security": "security",
    "identity": "security",
    "security": "security",
    "containers": "container",
    "container": "container",
    "developerservices": "developer",
    "developer services": "developer",
    "developer": "developer",
    "devops": "developer",
    "governance": "governance",
    "monitoring": "monitoring",
    "monitoringmanagement": "monitoring",
    "observabilityandmanagement": "monitoring",
    "observability&management": "monitoring",
    "observabilitymanagement": "monitoring",
    "analyticsai": "ai",
    "analytics&ai": "ai",
    "analyticsandai": "ai",
    "analytics": "ai",
    "ai": "ai",
    "migration": "migration",
    "hybrid": "hybrid",
    "applications": "applications",
    "edge": "networking",
    "connectivity": "networking",
    "groups": "groups",
    "marketplace": "applications",
    "other": "general",
    "ociuploadedtoomm": "general",
}

OCI_NAME_OVERRIDES = {
    "virtualcloudnetworkvcn": "VCN",
    "virtualcloudnetwork": "VCN",
    "vcn": "VCN",
    "internetgateway": "Internet Gateway",
    "natgateway": "NAT Gateway",
    "servicegateway": "Service Gateway",
    "dynamicroutinggatewaydrg": "DRG",
    "dynamicroutinggateway": "DRG",
    "drg": "DRG",
    "loadbalancerlb": "Load Balancer",
    "loadbalancer": "Load Balancer",
    "networkloadbalancernlb": "Network Load Balancer",
    "virtualmachine": "VM Instance",
    "virtualmachinevm": "VM (Desktop)",
    "baremetalcompute": "Bare Metal",
    "baremetal": "Bare Metal",
    "autoscaling": "Autoscaling",
    "functions": "Functions",
    "instancepools": "Instance Pools",
    "autonomousdatabase": "Autonomous Database",
    "mysqldatabasesystem": "MySQL HeatWave",
    "mysql": "MySQL HeatWave",
    "dbsystem": "DB System",
    "databasesystem": "DB System",
    "objectstorage": "Object Storage",
    "blockstorage": "Block Volume",
    "blockvolume": "Block Volume",
    "filestorage": "File Storage",
    "buckets": "Buckets",
    "webapplicationfirewallwaf": "WAF",
    "waf": "WAF",
    "firewall": "Network Firewall",
    "vault": "Vault",
    "keymanagement": "Key Management",
    "bastion": "Bastion",
    "iam": "IAM",
    "containerengine": "OKE",
    "containerengineforkubernetes": "OKE",
    "oke": "OKE",
    "containerinstances": "Container Instances",
    "containerinstance": "Container Instances",
    "containers": "Container Instances",
    "containerregistry": "OCIR",
    "ocir": "OCIR",
    "dns": "DNS",
    "cdn": "CDN",
    "streaming": "Streaming",
    "notifications": "Notifications",
    "logging": "Logging",
    "monitoring": "Monitoring",
    "events": "Events",
    "audit": "Audit",
}

AWS_SERVICE_CATEGORY_MAP = {
    "Arch_Analytics": "analytics",
    "Arch_Application-Integration": "applications",
    "Arch_Artificial-Intelligence": "ai",
    "Arch_Blockchain": "blockchain",
    "Arch_Business-Applications": "applications",
    "Arch_Cloud-Financial-Management": "governance",
    "Arch_Compute": "compute",
    "Arch_Containers": "container",
    "Arch_Customer-Enablement": "applications",
    "Arch_Databases": "database",
    "Arch_Developer-Tools": "developer",
    "Arch_End-User-Computing": "applications",
    "Arch_Front-End-Web-Mobile": "applications",
    "Arch_Games": "applications",
    "Arch_General-Icons": "general",
    "Arch_Internet-of-Things": "iot",
    "Arch_Management-Tools": "monitoring",
    "Arch_Media-Services": "applications",
    "Arch_Migration-Modernization": "migration",
    "Arch_Networking-Content-Delivery": "networking",
    "Arch_Quantum-Technologies": "quantum",
    "Arch_Satellite": "networking",
    "Arch_Security-Identity": "security",
    "Arch_Storage": "storage",
}

AWS_GROUP_NAME_OVERRIDES = {
    "virtualprivatecloudvpc": "VPC",
    "publicsubnet": "Public Subnet",
    "privatesubnet": "Private Subnet",
    "region": "Region",
    "awsaccount": "AWS Account",
    "awscloud": "AWS Cloud",
    "awscloudlogo": "AWS Cloud Logo",
    "awscloudlogodark": "AWS Cloud",
    "ec2instancecontents": "EC2 Instance Contents",
    "servercontents": "Server Contents",
}

AWS_GROUP_CATEGORY_OVERRIDES = {
    "VPC": "networking",
    "Public Subnet": "networking",
    "Private Subnet": "networking",
    "Region": "general",
    "AWS Account": "governance",
    "AWS Cloud": "general",
    "Auto Scaling Group": "compute",
    "Spot Fleet": "compute",
    "EC2 Instance Contents": "compute",
    "Server Contents": "compute",
    "Corporate Data Center": "hybrid",
}

AWS_NAME_OVERRIDES = {
    "amazonapigateway": "Amazon API Gateway",
    "amazoncloudfront": "Amazon CloudFront",
    "amazoncloudwatch": "Amazon CloudWatch",
    "amazonfsx": "Amazon FSx",
    "amazonfsxforlustre": "Amazon FSx for Lustre",
    "amazonfsxfornetappontap": "Amazon FSx for NetApp ONTAP",
    "amazonfsxforopenzfs": "Amazon FSx for OpenZFS",
    "amazonfsxforwfs": "Amazon FSx for Windows File Server",
    "amazonmanagedserviceforprometheus": "Amazon Managed Service for Prometheus",
    "amazonopensearchservice": "Amazon OpenSearch Service",
    "amazonroute53": "Amazon Route 53",
    "amazonsimplestorageservice": "Amazon Simple Storage Service",
    "amazonsimplestorageserviceglacier": "Amazon Simple Storage Service Glacier",
    "awsappconfig": "AWS AppConfig",
    "awscloudformation": "AWS CloudFormation",
    "awscloudtrail": "AWS CloudTrail",
    "awsdevopsagent": "AWS DevOps Agent",
    "awsdirectconnect": "AWS Direct Connect",
    "awsprivatelink": "AWS PrivateLink",
    "redhatopenshiftserviceonaws": "Red Hat OpenShift Service on AWS",
}

TOKEN_OVERRIDES = {
    "api": "API",
    "ec2": "EC2",
    "ecs": "ECS",
    "eks": "EKS",
    "ebs": "EBS",
    "efs": "EFS",
    "elb": "ELB",
    "iam": "IAM",
    "iot": "IoT",
    "kms": "KMS",
    "rds": "RDS",
    "s3": "S3",
    "sns": "SNS",
    "sqs": "SQS",
    "vpc": "VPC",
    "vpn": "VPN",
    "waf": "WAF",
    "aws": "AWS",
}

AWS_SIZE_PRIORITY = {"64": 4, "48": 3, "32": 2, "16": 1}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=["oci", "aws"])
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--icons-output", required=True)
    parser.add_argument("--components-output", required=True)
    parser.add_argument("--index-output", required=True)
    parser.add_argument("--category-dir", required=True)
    return parser.parse_args()


def normalize_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def split_words(text: str) -> list[str]:
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
    return [token for token in text.split() if token]


def title_token(token: str) -> str:
    lowered = token.lower()
    if lowered in TOKEN_OVERRIDES:
        return TOKEN_OVERRIDES[lowered]
    if token.isupper() and len(token) <= 4:
        return token
    return token.capitalize()


def humanize(text: str) -> str:
    return " ".join(title_token(token) for token in split_words(text))


def strip_svg_metadata(svg_text: str) -> str:
    svg_text = re.sub(r"<\?xml[^?]*\?>\s*", "", svg_text)
    svg_text = re.sub(r"<metadata[\s\S]*?</metadata>", "", svg_text, flags=re.IGNORECASE)
    svg_text = re.sub(r"<!--[\s\S]*?-->", "", svg_text)
    svg_text = re.sub(r">\s+<", "><", svg_text)
    return svg_text.strip()


def svg_to_data_uri(svg_path: Path) -> str:
    raw = svg_path.read_bytes()
    for encoding in ("utf-8", "latin-1"):
        try:
            svg_text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        svg_text = raw.decode("utf-8", errors="ignore")
    stripped = strip_svg_metadata(svg_text)
    payload = base64.b64encode(stripped.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml,{payload}"


def build_style(data_uri: str) -> str:
    return (
        "shape=image;verticalLabelPosition=bottom;labelBackgroundColor=none;"
        "labelPosition=center;verticalAlign=top;aspect=fixed;imageAspect=0;"
        f"image={data_uri};"
    )


def oci_filename_key(filename: str) -> str:
    name = Path(filename).stem
    name = re.sub(r"^oci[_-]?", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[_-]?(red|white|grey|gray|black|colored?)$", "", name, flags=re.IGNORECASE)
    return normalize_key(name)


def oci_display_name(filename: str) -> str:
    key = oci_filename_key(filename)
    if key in OCI_NAME_OVERRIDES:
        return OCI_NAME_OVERRIDES[key]
    name = Path(filename).stem
    name = re.sub(r"^OCI\s+", "", name, flags=re.IGNORECASE)
    return humanize(name)


def oci_category(parts: list[str]) -> str:
    category = "general"
    for part in parts:
        lowered = part.lower().replace(" ", "").replace("-", "").replace("_", "")
        if lowered in ("svg", "png", "icons", "ociicons", "oci", "red", "white", "grey", "gray", "black", "color", "colored"):
            continue
        category = OCI_CATEGORY_MAP.get(lowered, category if lowered == "" else lowered)
        if lowered in OCI_CATEGORY_MAP:
            break
    return category


def scan_oci(input_root: Path) -> list[dict[str, str | int]]:
    selected: dict[str, tuple[int, Path, str, str]] = {}
    for dirpath, _dirnames, filenames in os.walk(input_root):
        rel_parts = list(Path(dirpath).relative_to(input_root).parts)
        category = oci_category(rel_parts)
        for filename in sorted(filenames):
            if not filename.lower().endswith(".svg") or filename.startswith("._") or filename.startswith("."):
                continue
            key = oci_filename_key(filename)
            if not key:
                continue
            path = Path(dirpath) / filename
            display_name = oci_display_name(filename)
            lowered_path = str(path).lower()
            priority = 10 if "/red/" in lowered_path or "_red" in lowered_path else 5 if "/color/" in lowered_path else 1
            current = selected.get(key)
            if current is None or priority > current[0]:
                selected[key] = (priority, path, category, display_name)
    return [
        {"path": str(path), "category": category, "name": display_name}
        for _key, (_priority, path, category, display_name) in sorted(selected.items(), key=lambda item: item[1][3].lower())
    ]


def aws_service_key(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^Arch_", "", stem)
    stem = re.sub(r"_(16|32|48|64)$", "", stem)
    return normalize_key(stem)


def aws_service_name(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^Arch_", "", stem)
    stem = re.sub(r"_(16|32|48|64)$", "", stem)
    key = normalize_key(stem)
    if key in AWS_NAME_OVERRIDES:
        return AWS_NAME_OVERRIDES[key]
    return humanize(stem)


def aws_group_key(filename: str) -> str:
    stem = Path(filename).stem
    dark = bool(re.search(r"_(16|32|48|64)_Dark$", stem))
    stem = re.sub(r"_(16|32|48|64)(?:_Dark)?$", "", stem)
    return normalize_key(stem + ("Dark" if dark else ""))


def aws_group_name(filename: str) -> str:
    stem = Path(filename).stem
    dark = bool(re.search(r"_(16|32|48|64)_Dark$", stem))
    stem = re.sub(r"_(16|32|48|64)(?:_Dark)?$", "", stem)
    key = normalize_key(stem)
    if key in AWS_GROUP_NAME_OVERRIDES:
        base = AWS_GROUP_NAME_OVERRIDES[key]
    else:
        base = humanize(stem)
    return f"{base} Dark" if dark else base


def scan_aws(input_root: Path) -> list[dict[str, str | int]]:
    selected: dict[tuple[str, str], tuple[int, Path, str, str]] = {}

    for path in input_root.rglob("*.svg"):
        if path.name.startswith("._") or path.name.startswith("."):
            continue
        if "__MACOSX" in path.parts:
            continue

        parts = path.parts
        if any(part.startswith("Architecture-Service-Icons_") for part in parts):
            category_dir = next((part for part in parts if part.startswith("Arch_")), None)
            if category_dir is None:
                continue
            category = AWS_SERVICE_CATEGORY_MAP.get(category_dir, normalize_key(category_dir.replace("Arch_", "")))
            size_dir = next((part for part in parts if part in AWS_SIZE_PRIORITY), "16")
            priority = AWS_SIZE_PRIORITY.get(size_dir, 0)
            key = ("service", aws_service_key(path.name))
            display_name = aws_service_name(path.name)
        elif any(part.startswith("Architecture-Group-Icons_") for part in parts):
            category = "general"
            priority = 2
            key = ("group", aws_group_key(path.name))
            display_name = aws_group_name(path.name)
            category = AWS_GROUP_CATEGORY_OVERRIDES.get(display_name, category)
        else:
            continue

        current = selected.get(key)
        if current is None or priority > current[0]:
            selected[key] = (priority, path, category, display_name)

    return [
        {"path": str(path), "category": category, "name": display_name}
        for _key, (_priority, path, category, display_name) in sorted(selected.items(), key=lambda item: item[1][3].lower())
    ]


def write_outputs(entries: list[dict[str, str | int]], icons_output: Path, components_output: Path, index_output: Path, category_dir: Path) -> None:
    library_entries = []
    components: dict[str, dict[str, str | int]] = {}
    by_category: dict[str, dict[str, dict[str, str | int]]] = defaultdict(dict)

    for entry in entries:
        path = Path(str(entry["path"]))
        category = str(entry["category"])
        name = str(entry["name"])
        data_uri = svg_to_data_uri(path)
        style = build_style(data_uri)

        library_entries.append({"data": data_uri, "w": 60, "h": 60, "title": name, "aspect": "fixed"})
        component = {
            "style": style,
            "width": 60,
            "height": 60,
            "category": category,
            "description": name,
            "svg_file": path.name,
        }
        components[name] = component
        by_category[category][name] = component

    icons_output.parent.mkdir(parents=True, exist_ok=True)
    components_output.parent.mkdir(parents=True, exist_ok=True)
    index_output.parent.mkdir(parents=True, exist_ok=True)
    category_dir.mkdir(parents=True, exist_ok=True)

    icons_output.write_text(f"<mxlibrary>{json.dumps(library_entries, separators=(',', ':'))}</mxlibrary>\n", encoding="utf-8")
    components_output.write_text(json.dumps(components, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    index = {name: component["category"] for name, component in components.items()}
    index_output.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for category, category_components in sorted(by_category.items()):
        target = category_dir / f"{category}.json"
        target.write_text(json.dumps(category_components, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_root = Path(args.input_root)
    if not input_root.exists():
        print(f"Input root not found: {input_root}", file=sys.stderr)
        return 1

    if args.provider == "oci":
        entries = scan_oci(input_root)
    else:
        entries = scan_aws(input_root)

    if not entries:
        print(f"No SVG icons found for provider={args.provider} under {input_root}", file=sys.stderr)
        return 1

    write_outputs(
        entries,
        Path(args.icons_output),
        Path(args.components_output),
        Path(args.index_output),
        Path(args.category_dir),
    )

    print(f"Generated {len(entries)} {args.provider.upper()} components", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
