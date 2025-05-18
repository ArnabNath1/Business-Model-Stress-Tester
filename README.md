# Business Model Stress Tester 🚀

An AI-powered tool that analyzes business models through multiple scenarios to identify vulnerabilities and provide strategic recommendations.

## 🌟 Features

- 🤖 **AI-Powered Analysis**
  - Dynamic scenario generation
  - Vulnerability assessment
  - Risk scoring and prioritization
  - Strategic recommendations

- 📊 **Comprehensive Reports**
  - Executive summaries
  - Risk heat maps
  - Scenario analysis
  - Implementation roadmaps

- 🔄 **Flexible Input Options**
  - Interactive CLI interface
  - JSON file input
  - Custom configuration
  - Markdown report output

## 📋 Requirements

- Python 3.8+
- OpenRouter API key
- Required packages:
  ```bash
  python-dotenv==1.0.0
  requests==2.31.0
  ```

## 🚀 Quick Start

1. **Clone & Setup**
   ```bash
   git clone https://github.com/yourusername/business-model-stress-tester.git
   cd business-model-stress-tester
   pip install -r requirements.txt
   ```

2. **Configure API Key**
   Create `.env` file:
   ```properties
   OPENROUTER_API_KEY=your_api_key_here
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   ```

3. **Run Analysis**
   ```bash
   python business_model_stress_tester.py
   ```

## 💡 Usage Examples

### Interactive Mode
```bash
python business_model_stress_tester.py
```

### Using JSON Input
```bash
python business_model_stress_tester.py --input model.json
```

### Custom Output Location
```bash
python business_model_stress_tester.py --output custom_report.md
```

## 📁 Project Structure

```
business-model-stress-tester/
├── business_model_stress_tester.py  # Main script
├── requirements.txt                 # Dependencies
├── examples/                        # Example files
│   ├── sample_model.json           # Sample input
│   └── sample_report.md            # Sample output
├── .env                            # API configuration
└── README.md                       # Documentation
```

## 📝 Input Format

```json
{
  "name": "Tech Startup",
  "industry": "SaaS",
  "target_market": "Small Businesses",
  "value_proposition": "AI-powered automation",
  "revenue_streams": ["Subscriptions", "Setup fees"],
  "cost_structure": ["Development", "Marketing"],
  "key_resources": ["Dev Team", "AI Models"],
  "key_partners": ["Cloud Providers"],
  "competitors": ["BigCorp", "StartupX"],
  "current_challenges": "High customer acquisition costs"
}
```

## 🔍 Troubleshooting

- **API Key Error**: Check `.env` file configuration
- **JSON Parse Error**: Validate input JSON format
- **Model Error**: Ensure OpenRouter API access
- **Report Generation**: Check write permissions

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 🆘 Support

- 📚 Check [Documentation](docs/)
- 🐛 Report [Issues](https://github.com/yourusername/business-model-stress-tester/issues)
- 📧 Contact: your.email@domain.com

## 🙏 Acknowledgments

- OpenRouter API team
- Contributors & maintainers
- Open source community