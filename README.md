# oci-skills

OCI（Oracle Cloud Infrastructure）向けの AI コーディングアシスタント用 **Skills コレクション**です。

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) と [Codex（OpenAI）](https://openai.com/index/introducing-codex/) の両方で利用できます。スキルをインストールすると、AI アシスタントが OCI 関連の作業を自動化・効率化してくれます。`oci-drawio` は OCI ネイティブ図に加えて、AWS リソース図や OCI/AWS 混在図にも対応しています。

---

## 収録スキル

### oci-drawio — OCI / AWS 構成図ジェネレーター

自然言語の指示から **draw.io 形式（.drawio）の OCI アーキテクチャ構成図**を自動生成するスキルです。OCI 標準レイアウトをベースにしつつ、AWS 公式アイコンパッケージを使った AWS ネイティブ図や混在図も生成できます。

- 「3層Webアプリのアーキテクチャ図を描いて」のような指示で構成図を生成
- 既存の `.drawio` ファイルを読み込んで編集・追記も可能
- Oracle 公式の OCI アイコンと AWS 公式の AWS Architecture Icons を使用
- Region → VCN → Subnet → Service の OCI 標準レイアウトに自動配置
- AWS の場合は Region → VPC → Subnet 構成と `components/aws/` の辞書を使用

#### 対応コンポーネント

| カテゴリ | コンポーネント |
|---------|-------------|
| **Networking** | VCN, Subnet, Internet Gateway, NAT Gateway, Service Gateway, DRG, Load Balancer, Network Load Balancer, DNS, FastConnect, VPN |
| **Compute** | VM Instance, Bare Metal, Autoscaling, Instance Pools, Functions |
| **Database** | Autonomous Database, MySQL HeatWave, DB System, Exadata |
| **Storage** | Object Storage, Block Volume, File Storage, Buckets |
| **Security** | WAF, Network Firewall, Vault, Bastion, IAM |
| **Container** | OKE, Container Instances, OCIR |
| **Monitoring** | Streaming, Notifications, Logging, Monitoring |

AWS 向けには `components/aws/` 以下に `networking`, `compute`, `container`, `database`, `storage`, `security` などのカテゴリ辞書が生成され、`Amazon API Gateway`, `AWS Lambda`, `Amazon ECS`, `Amazon RDS`, `Amazon S3`, `VPC`, `Public Subnet`, `Private Subnet` などが利用できます。

#### サンプル構成図

`skills/oci-drawio/examples/` にサンプルが含まれています。

- **basic-web-3tier.drawio** — 基本的な 3 層 Web アーキテクチャ（LB + Web + App + ADB）
- **ha-architecture.drawio** — 高可用性構成（WAF、冗長 Web/App サーバー、Data Guard）

---

## インストール

### 前提条件

- Git
- Bash

### 手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/araidon/oci-skills.git
cd oci-skills

# 2. スキルをインストール
./install.sh oci-drawio
```

### install.sh のオプション

```bash
# Claude Code にインストール（デフォルト）
./install.sh oci-drawio

# Codex にインストール（グローバル）
./install.sh oci-drawio --tool codex

# Codex にインストール（プロジェクトローカル）
./install.sh oci-drawio --tool codex-local

# Codex にインストール（リポジトリスキャン用）
./install.sh oci-drawio --tool codex-repo

# 利用可能なスキル一覧
./install.sh --list

# 全スキルを一括インストール
./install.sh --all
```

| インストール先 | パス | 用途 |
|--------------|------|------|
| Claude Code | `~/.claude/skills/<name>/` | Claude Code で利用 |
| Codex（グローバル） | `~/.codex/skills/<name>/` | 全プロジェクトで利用 |
| Codex（プロジェクト） | `.codex/skills/<name>/` | 特定プロジェクトで利用 |
| Codex（リポジトリ） | `.agents/skills/<name>/` | リポジトリスキャン |

---

## セットアップ（oci-drawio）

インストール後、初回のみセットアップスクリプトを実行して OCI / AWS の公式アイコンを取得する必要があります。

### 必要なツール

- `curl`
- `unzip`
- `base64`
- `uv`

### 実行

```bash
cd ~/.claude/skills/oci-drawio    # インストール先に移動
bash setup.sh --provider all
```

セットアップが完了すると以下が生成されます：

- `icons/oci-shapes.xml` — draw.io 用カスタムアイコンライブラリ
- `icons/aws-shapes.xml` — AWS 用カスタムアイコンライブラリ
- `components/oci_components.json` — OCI コンポーネント辞書（スタイル情報付き）
- `components/aws_components.json` — AWS コンポーネント辞書（スタイル情報付き）
- `components/index.json` / `components/{category}.json` — OCI 用の軽量インデックスとカテゴリ分割
- `components/aws/index.json` / `components/aws/{category}.json` — AWS 用の軽量インデックスとカテゴリ分割

---

## 使い方

インストールとセットアップが完了すれば、AI アシスタントに指示するだけで構成図を生成できます。

### Claude Code での例

```
> OCI上に3層Webアプリの構成図を描いてください。
> LBの後ろにWebサーバー2台、プライベートサブネットにAppサーバーとAutonomous Databaseを配置してください。

> AWS上に ALB / ECS / RDS / S3 の構成図を描いてください。
> Public Subnet と Private Subnet を明示して、Object Storage はリージョンサービスとして表現してください。
```

### 既存ファイルの編集

```
> web-architecture.drawio にNATゲートウェイを追加してください。
> 既存の構成図にWAFとBastionを追加して、高可用性構成にしてください。
```

生成された `.drawio` ファイルは [draw.io](https://app.diagrams.net/)（デスクトップ版・Web版）でそのまま開けます。

---

## 注意事項

- OCI アイコンは Oracle 公式サイトから、AWS アイコンは AWS 公式サイトからダウンロードしています。利用にあたっては各ベンダーのブランドガイドラインに従ってください。
- `setup.sh` の実行にはインターネット接続が必要です。
- draw.io の MCP サーバーは使用せず、XML テキストを直接生成する方式を採用しています。そのため追加のサーバー設定は不要です。

---

## ライセンス

このリポジトリのコードは MIT License で公開されています。

OCI アイコンの著作権は Oracle Corporation に帰属します。
AWS アイコンの著作権は Amazon Web Services, Inc. に帰属します。
