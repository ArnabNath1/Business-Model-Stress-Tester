#!/usr/bin/env python3
"""
Business Model Stress-Tester

This script uses the Groq API to analyze a business model and simulate various
market conditions, competitor moves, and economic scenarios to identify vulnerabilities
and suggest contingency plans.

Requirements:
- python-dotenv (for environment variables)
- groq package (for Groq API)
"""

import os
import json
import time
import argparse
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import groq
import re


# Load environment variables from .env file
load_dotenv()

# Configure API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables or .env file")

# Configure the Groq client
client = groq.Client(api_key=GROQ_API_KEY)

# Define the model to use
MODEL_CONFIG = {
    "name": "gemma2-9b-it",  # Better model for structured output
    "max_tokens": 4096,
    "temperature": 0.7,
    "response_format": {"type": "json"}  # Request JSON formatted responses
}

class BusinessModelStressTester:
    """Class to handle business model stress testing using Groq API."""
    
    def __init__(self):
        """Initialize the stress tester with the Groq model."""
        self.client = client
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
    
    def generate_scenarios(self, business_model: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate various scenarios to stress test the business model."""
        prompt = f"""
        Based on the following business model, generate realistic stress test scenarios in these categories:
        1. Market Conditions (economic downturns, market shifts, etc.)
        2. Competitor Moves (new entrants, pricing strategies, etc.)
        3. Supply Chain Disruptions
        4. Regulatory Changes
        5. Technology Shifts
        6. Consumer Behavior Changes
        
        For each category, provide 3-5 specific, realistic scenarios that could impact this business.
        
        Business Model Details:
        {json.dumps(business_model, indent=2)}
        
        Format your response as a JSON object with categories as keys and lists of scenarios as values.
        """
        
        print("\nGenerating stress test scenarios...")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a business analyst expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"]
        )
        
        response_text = completion.choices[0].message.content
        
        try:
            # Extract JSON from the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                scenarios = json.loads(json_content)
            else:
                # Fallback if JSON parsing fails
                scenarios = self._parse_scenarios_from_text(response_text)
        except Exception as e:
            print(f"Error parsing scenarios: {e}")
            # Fallback to text parsing
            scenarios = self._parse_scenarios_from_text(response_text)
            
        return scenarios
    
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
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a business analyst. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.5,  # Lower temperature for more consistent JSON
                    max_tokens=2000,
                    response_format={"type": "json"}  # Request JSON response
                )
                
                response_text = completion.choices[0].message.content
                
                # Clean and parse JSON
                json_content = self._clean_json_response(response_text)
                chunk_analysis = json.loads(json_content)
                
                # Merge chunk results
                if "scenarios" in chunk_analysis:
                    combined_analysis["scenarios"].update(chunk_analysis["scenarios"])
                if "chunk_summary" in chunk_analysis:
                    combined_analysis["summary"].append(chunk_analysis["chunk_summary"])
                    
            except Exception as e:
                print(f"Error processing chunk: {str(e)}")
                # Add error information to analysis
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
        """
        Generate a comprehensive report with the analysis results.
        
        Args:
            business_model: Dictionary containing business model details.
            scenarios: Dictionary of stress test scenarios.
            analysis: Dictionary containing vulnerability analysis.
            
        Returns:
            String containing the formatted report.
        """
        prompt = f"""
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
        
        print("\nGenerating comprehensive report...")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a business analyst expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=MODEL_CONFIG["temperature"],
            max_tokens=MODEL_CONFIG["max_tokens"]
        )
        
        return completion.choices[0].message.content
    
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

