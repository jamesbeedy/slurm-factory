
# Contact & Support

Get help, report issues, or connect with the slurm-factory community.

## Getting Help

### 📚 Documentation
Start with our comprehensive documentation:
- **[Installation Guide](/slurm-factory/installation/)** - Setup and configuration
- **[Troubleshooting](/slurm-factory/troubleshooting/)** - Common issues and solutions
- **[API Reference](/slurm-factory/api-reference/)** - Complete API documentation
- **[Architecture Guide](/slurm-factory/architecture/)** - Technical deep-dive

### 💬 Community Support

#### GitHub Discussions
**Best for**: General questions, usage help, feature discussions
- **URL**: [github.com/vantagecompute/slurm-factory/discussions](https://github.com/vantagecompute/slurm-factory/discussions)
- **Categories**:
  - **Q&A**: Usage questions and help
  - **Ideas**: Feature requests and suggestions
  - **Show and tell**: Share your deployments
  - **General**: General discussion

#### GitHub Issues
**Best for**: Bug reports, specific problems, feature requests
- **URL**: [github.com/vantagecompute/slurm-factory/issues](https://github.com/vantagecompute/slurm-factory/issues)
- **Templates**: We provide issue templates for:
  - Bug reports
  - Feature requests
  - Documentation improvements

### 🚀 Quick Help

#### Before Asking for Help

1. **Check documentation**: Search our docs for your issue
2. **Review troubleshooting**: Common issues are covered in the [troubleshooting guide](/slurm-factory/troubleshooting/)
3. **Search existing issues**: Your question might already be answered
4. **Try different versions**: Test with different Slurm versions

#### When Asking for Help

Include this information:
```bash
# System information
uname -a                    # OS and kernel
python3 --version          # Python version
lxd --version              # LXD version
uv --version               # UV version

# slurm-factory information
uv run slurm-factory --version

# Error logs (if applicable)
cat ~/.slurm-factory/logs/latest.log

# Environment variables
env | grep -E "(SLURM_FACTORY|LXD)"
```

## Bug Reports

### 🐛 Reporting Bugs

**Use**: [GitHub Issues](https://github.com/vantagecompute/slurm-factory/issues/new/choose)

**Include**:
1. **Clear description**: What you expected vs what happened
2. **Steps to reproduce**: Minimal steps to reproduce the issue
3. **Environment**: OS, Python, LXD versions
4. **Logs**: Error messages and relevant log files
5. **Workarounds**: Any temporary solutions you've found

**Example Bug Report**:
```markdown
## Bug Description
Build fails for Slurm 25.05 with GPU support on Ubuntu 22.04

## Steps to Reproduce
1. `uv run slurm-factory build 25.05 --gpu`
2. Build fails after ~30 minutes with CUDA errors

## Environment
- OS: Ubuntu 22.04.3 LTS
- Python: 3.11.6
- LXD: 5.16
- UV: 0.1.18

## Error Log
```
[ERROR] CUDA toolkit installation failed
...
```

## Expected Behavior
Build should complete successfully with GPU support

## Actual Behavior
Build fails with CUDA-related errors
```

### 🔍 Security Issues

For security vulnerabilities:
- **Email**: security@vantagecompute.ai
- **Include**: Detailed description and impact assessment
- **Response time**: We aim to respond within 24 hours

## Feature Requests

### 💡 Suggesting Features

**Use**: [GitHub Discussions - Ideas](https://github.com/vantagecompute/slurm-factory/discussions/categories/ideas)

**Include**:
1. **Use case**: Why you need this feature
2. **Proposed solution**: How you think it should work
3. **Alternatives**: Other solutions you've considered
4. **Examples**: Similar features in other tools

**Example Feature Request**:
```markdown
## Feature Request: Cross-compilation Support

### Use Case
Build Slurm packages for ARM64 clusters from x86_64 build machines

### Proposed Solution
Add `--target-arch` option to specify target architecture:
`uv run slurm-factory build 25.05 --target-arch arm64`

### Alternatives Considered
- Building directly on ARM64 (slow, expensive)
- Using emulation (very slow)

### Examples
- Docker buildx multi-platform builds
- Cross-compilation in other package managers
```

## Commercial Support

### 🏢 Enterprise Support

For commercial deployments and enterprise support:
- **Company**: Vantage Compute
- **Website**: [vantagecompute.ai](https://vantagecompute.ai)
- **Email**: support@vantagecompute.ai

**Services**:
- Custom Slurm configurations
- Large-scale deployment assistance
- Performance optimization consulting
- Priority support and bug fixes
- Training and professional services

### 📈 Consulting Services

- **HPC Architecture Design**: Cluster planning and optimization
- **Migration Services**: Moving from other schedulers to Slurm
- **Performance Tuning**: Optimizing Slurm for your workloads
- **Custom Development**: Feature development and integration

## Contributing

### 🤝 Get Involved

Want to contribute? We welcome:
- **Code contributions**: Bug fixes, new features
- **Documentation**: Improvements and examples
- **Testing**: Testing new features and releases
- **Community support**: Helping other users

**Start here**: [Contributing Guide](/slurm-factory/contributing/)

### 👥 Maintainers

- **Core Team**: Vantage Compute team
- **Lead Maintainer**: Available via GitHub
- **Community**: Active contributors and users

## Response Times

### Community Support
- **GitHub Discussions**: Usually within 1-2 days
- **GitHub Issues**: Usually within 2-3 days
- **Documentation**: Updates within 1 week

### Commercial Support
- **Critical Issues**: Within 4 hours
- **Standard Issues**: Within 1 business day
- **Feature Requests**: Within 1 week

## Useful Links

### Project Resources
- **Repository**: [github.com/vantagecompute/slurm-factory](https://github.com/vantagecompute/slurm-factory)
- **Documentation**: [vantagecompute.github.io/slurm-factory](https://vantagecompute.github.io/slurm-factory)
- **Releases**: [github.com/vantagecompute/slurm-factory/releases](https://github.com/vantagecompute/slurm-factory/releases)

### Related Projects
- **Slurm**: [slurm.schedmd.com](https://slurm.schedmd.com)
- **Spack**: [spack.io](https://spack.io)
- **LXD**: [linuxcontainers.org/lxd](https://linuxcontainers.org/lxd)
- **Environment Modules**: [modules.readthedocs.io](https://modules.readthedocs.io)

## Stay Updated

### 📢 Announcements
- **GitHub Releases**: Watch the repository for release notifications
- **GitHub Discussions**: Follow announcement category
- **Company Blog**: [vantagecompute.ai/blog](https://vantagecompute.ai/blog)

### 🔔 Notifications
Configure GitHub notifications for:
- New releases
- Issue mentions
- Discussion replies

