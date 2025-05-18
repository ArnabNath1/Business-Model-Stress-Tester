#!/usr/bin/env python3
"""
Business Model Stress-Tester

This script uses the OpenAI API to analyze a business model and simulate various
market conditions, competitor moves, and economic scenarios to identify vulnerabilities
and suggest contingency plans.

Requirements:
- python-dotenv (for environment variables)
- openai package (for OpenAI API)
"""

import os
import re
import json
import time
import argparse
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Configure OpenRouter API
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in environment variables")

# Model configuration
MODEL_CONFIG = {
    "name": "qwen/qwen3-0.6b-04-28:free",  # One of OpenRouter's best models
    "max_tokens": 4000,
    "temperature": 0.7
}

class BusinessModelStressTester:
    """Class to handle business model stress testing using OpenRouter API."""
    
    def __init__(self):
        """Initialize the stress tester with OpenRouter configuration."""
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            # "HTTP-Referer": "https://github.com/yourusername/business-model-stress-tester",
            "Content-Type": "application/json"
        }
        self.model = MODEL_CONFIG["name"]
        
    def get_business_model_details(self) -> Dict[str, Any]:
        """
        Collect business model details from user input.
        
        Returns:
            Dict containing the business model details.
        """
        print("\n" + "="*80)
        print("BUSINESS MODEL STRESS TESTER".center(80))
        print("="*80 + "\n")
        
        print("Please provide details about your business model:\n")
        
        business_model = {
            "name": input("Business Name: "),
            "industry": input("Industry: "),
            "target_market": input("Target Market/Customer Segment: "),
            "value_proposition": input("Value Proposition: "),
            "revenue_streams": input("Revenue Streams (comma separated): ").split(","),
            "cost_structure": input("Major Cost Components (comma separated): ").split(","),
            "key_resources": input("Key Resources (comma separated): ").split(","),
            "key_partners": input("Key Partners/Suppliers (comma separated): ").split(","),
            "competitors": input("Main Competitors (comma separated): ").split(","),
            "current_challenges": input("Current Business Challenges: "),
        }
        
        # Optional: Add financial metrics if available
        add_financials = input("\nWould you like to add financial metrics? (y/n): ").lower()
        if add_financials == 'y':
            business_model["financials"] = {
                "annual_revenue": input("Annual Revenue (USD): "),
                "profit_margin": input("Profit Margin (%): "),
                "burn_rate": input("Monthly Burn Rate (if applicable): "),
                "runway": input("Runway in months (if applicable): "),
            }
            
        return business_model
    
    def _make_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Make a request to OpenRouter API."""
        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": MODEL_CONFIG["max_tokens"],
                    "temperature": MODEL_CONFIG["temperature"]
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ValueError(f"OpenRouter API request failed: {str(e)}")

    def generate_scenarios(self, business_model: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate stress test scenarios using OpenRouter."""
        prompt = f"""Generate stress test scenarios for this business model in strict JSON format.
        Business Model: {json.dumps(business_model, indent=2)}
        
        Return ONLY a JSON object with exactly this structure:
        {{
            "market_conditions": [
                "Scenario 1",
                "Scenario 2"
            ],
            "competitor_moves": [
                "Scenario 1",
                "Scenario 2"
            ],
            "supply_chain": [
                "Scenario 1",
                "Scenario 2"
            ],
            "regulatory": [
                "Scenario 1",
                "Scenario 2"
            ],
            "technology": [
                "Scenario 1",
                "Scenario 2"
            ]
        }}
        """
        
        messages = [
            {"role": "system", "content": "You are a business analyst expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            print("\nGenerating stress test scenarios...")
            response = self._make_request(messages)
            
            if not response or 'choices' not in response:
                raise ValueError("Invalid response structure from API")
                
            content = response['choices'][0]['message']['content']
            
            # Clean and extract JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end].strip()
                try:
                    scenarios = json.loads(json_str)
                    if not isinstance(scenarios, dict):
                        raise ValueError("Response is not a dictionary")
                    return scenarios
                except json.JSONDecodeError:
                    print("Failed to parse JSON response, using fallback structure")
            
            # Return default structure if parsing fails
            return {
                "market_conditions": [
                    f"Economic downturn affecting {business_model['industry']}",
                    "Market saturation and increased competition"
                ],
                "competitor_moves": [
                    "New competitor entry with innovative solution",
                    "Price war initiated by major competitor"
                ],
                "supply_chain": [
                    "Supply chain disruption",
                    "Raw material cost increase"
                ],
                "regulatory": [
                    f"New regulations in {business_model['industry']}",
                    "Changes in compliance requirements"
                ],
                "technology": [
                    "Disruptive technology emergence",
                    "Legacy system obsolescence"
                ]
            }
            
        except Exception as e:
            print(f"Error generating scenarios: {str(e)}")
            # Return basic scenario structure as fallback
            return {
                "market_conditions": ["Market downturn", "Competition increase"],
                "competitor_moves": ["New market entry", "Price competition"],
                "supply_chain": ["Supply disruption", "Cost increase"],
                "regulatory": ["New regulations", "Policy changes"],
                "technology": ["Tech disruption", "Innovation pressure"]
            }

    def _parse_scenarios_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Fallback method to parse scenarios from text if JSON parsing fails.
        
        Args:
            text: Response text from the API.
            
        Returns:
            Dictionary of scenario categories and lists.
        """
        categories = [
            "Market Conditions", 
            "Competitor Moves", 
            "Supply Chain Disruptions",
            "Regulatory Changes",
            "Technology Shifts",
            "Consumer Behavior Changes"
        ]
        
        result = {}
        current_category = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a category header
            for category in categories:
                if category in line or category.upper() in line:
                    current_category = category
                    result[current_category] = []
                    break
                    
            # If we have a current category and line starts with a number or dash, it's a scenario
            if current_category and (line.startswith(('-', '•', '*')) or 
                                    (line[0].isdigit() and line[1] in ['.', ')', ':'])):
                # Remove the bullet/number prefix
                scenario = line.split(' ', 1)[1] if ' ' in line else line
                result[current_category].append(scenario)
                
        return result
    
    def analyze_vulnerabilities(self, business_model: Dict[str, Any], 
                               scenarios: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze vulnerabilities in the business model based on the scenarios."""
        
        # Split the analysis into smaller chunks
        scenario_chunks = self.chunk_large_content(scenarios)
        combined_analysis = {
            "summary": [],
            "scenarios": {}
        }
        
        for chunk in scenario_chunks:
            prompt = f"""
            Analyze this portion of the business model scenarios.
            Provide analysis in strict JSON format.
            
            Business Model:
            {json.dumps(business_model, indent=2)}
            
            Scenarios to Analyze:
            {json.dumps(chunk, indent=2)}
            
            Format your response EXACTLY as this JSON structure:
            {{
                "scenarios": {{
                    "category_name": {{
                        "scenario_description": {{
                            "vulnerabilities": ["list"],
                            "impact": "High/Medium/Low",
                            "likelihood": "High/Medium/Low",
                            "risk_score": 1-10,
                            "contingency_plans": ["list"]
                        }}
                    }}
                }},
                "chunk_summary": "Brief summary of key risks in this chunk"
            }}
            """
            
            try:
                # Use _make_request instead of client
                response = self._make_request([
                    {"role": "system", "content": "You are a business analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ])
                
                content = response['choices'][0]['message']['content']
                
                # Clean and parse JSON
                json_content = self._clean_json_response(content)
                chunk_analysis = json.loads(json_content)
                
                # Merge chunk results
                if "scenarios" in chunk_analysis:
                    combined_analysis["scenarios"].update(chunk_analysis["scenarios"])
                if "chunk_summary" in chunk_analysis:
                    combined_analysis["summary"].append(chunk_analysis["chunk_summary"])
                    
            except Exception as e:
                print(f"Error processing chunk: {str(e)}")
                combined_analysis["errors"] = combined_analysis.get("errors", [])
                combined_analysis["errors"].append(str(e))
        
        return combined_analysis

    def _clean_json_response(self, response_text: str) -> str:
        """Clean and validate JSON response."""
        try:
            # Remove any text before the first '{' and after the last '}'
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                
                # Clean up common JSON issues
                json_content = re.sub(r'[\n\r\t]', ' ', json_content)  # Remove newlines and tabs
                json_content = re.sub(r'\s+', ' ', json_content)  # Normalize whitespace
                json_content = json_content.replace("'", '"')  # Replace single quotes
                json_content = re.sub(r'(\w+):', r'"\1":', json_content)  # Quote unquoted keys
                
                # Validate JSON
                json.loads(json_content)  # Test if valid
                return json_content
                
        except Exception as e:
            raise ValueError(f"Invalid JSON response: {str(e)}")
        
        raise ValueError("No valid JSON found in response")
    
    def generate_report(self, business_model: Dict[str, Any], 
                       scenarios: Dict[str, List[str]],
                       analysis: Dict[str, Any]) -> str:
        # Update to use _make_request instead of client
        print("\nGenerating comprehensive report...")
        response = self._make_request([
            {"role": "system", "content": "You are a business analyst expert."},
            {"role": "user", "content": self._create_report_prompt(business_model, scenarios, analysis)}
        ])
        
        return response['choices'][0]['message']['content']

    def _create_report_prompt(self, business_model: Dict[str, Any], 
                            scenarios: Dict[str, List[str]],
                            analysis: Dict[str, Any]) -> str:
        """Create the prompt for report generation."""
        return f"""
        Create a comprehensive business model stress test report based on the following information:
        
        Business Model:
        {json.dumps(business_model, indent=2)}
        
        Scenarios Tested:
        {json.dumps(scenarios, indent=2)}
        
        Analysis Results:
        {json.dumps(analysis, indent=2)}
        
        The report should include:
        1. Executive Summary
        2. Business Model Overview
        3. Methodology
        4. Key Findings by Scenario Category
        5. Risk Heat Map (describe which scenarios have highest impact/likelihood)
        6. Strategic Recommendations
        7. Implementation Roadmap
        
        Format the report in markdown for readability.
        """
    
    def run_stress_test(self, business_model: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the complete stress test process.
        
        Args:
            business_model: Optional dictionary with business model details.
                           If None, will prompt user for input.
                           
        Returns:
            String containing the final report.
        """
        if business_model is None:
            business_model = self.get_business_model_details()
            
        print("\nRunning business model stress test...")
        
        # Generate scenarios
        scenarios = self.generate_scenarios(business_model)
        
        # Display generated scenarios
        print("\nGenerated Stress Test Scenarios:")
        for category, scenario_list in scenarios.items():
            print(f"\n{category}:")
            for i, scenario in enumerate(scenario_list, 1):
                print(f"  {i}. {scenario}")
        
        # Analyze vulnerabilities
        analysis = self.analyze_vulnerabilities(business_model, scenarios)
        
        # Generate comprehensive report
        report = self.generate_report(business_model, scenarios, analysis)
        
        return report

    def validate_api_response(self, response_text: str) -> bool:
        """Validate API response for common issues."""
        if not response_text or len(response_text.strip()) < 10:
            return False
        
        # Check for error indicators
        error_indicators = ["error", "invalid", "failed"]
        if any(indicator in response_text.lower() for indicator in error_indicators):
            return False
            
        return True

    def chunk_large_content(self, content: Dict[str, Any], max_tokens: int = 1500) -> List[Dict[str, Any]]:
        """Split large content into manageable chunks."""
        chunks = []
        current_chunk = {}
        current_size = 0
        
        for key, value in content.items():
            # Estimate tokens (rough approximation)
            value_size = len(str(value)) // 4
            if current_size + value_size > max_tokens:
                chunks.append(current_chunk)
                current_chunk = {}
                current_size = 0
            current_chunk[key] = value
            current_size += value_size
        
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

def save_report(report: str, business_name: str) -> str:
    """
    Save the report to a markdown file.
    
    Args:
        report: String containing the report content.
        business_name: Name of the business for the filename.
        
    Returns:
        Path to the saved file.
    """
    # Create a sanitized filename
    filename = f"{business_name.lower().replace(' ', '_')}_stress_test_{time.strftime('%Y%m%d')}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
        
    return filename

def main():
    """Main function to run the business model stress tester."""
    parser = argparse.ArgumentParser(description='Business Model Stress Tester')
    parser.add_argument('--input', '-i', type=str, help='Path to JSON file with business model details')
    parser.add_argument('--output', '-o', type=str, help='Path to save the output report')
    args = parser.parse_args()
    
    stress_tester = BusinessModelStressTester()
    
    # Load business model from file if provided
    business_model = None
    if args.input:
        try:
            with open(args.input, 'r') as f:
                business_model = json.load(f)
            print(f"Loaded business model from {args.input}")
        except Exception as e:
            print(f"Error loading business model from file: {e}")
            business_model = None
    
    # Run the stress test
    report = stress_tester.run_stress_test(business_model)
    
    # Save the report
    if args.output:
        filename = args.output
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
    else:
        business_name = business_model['name'] if business_model and 'name' in business_model else "business"
        filename = save_report(report, business_name)
        
    print(f"\nStress test complete! Report saved to: {filename}")
    print("\nKey findings and recommendations are available in the report.")

if __name__ == "__main__":
    main()

