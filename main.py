#!/usr/bin/env python3
"""
AI Test Automation Assistant - Main Entry Point
Tam otomatik web sitesi test süreciği: URL -> HTML analizi -> AI BDD -> Test üretimi -> Rapor
"""

import argparse
import asyncio
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/automation.log", level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")

def check_dependencies():
    """Check if all dependencies are available"""
    try:
        import requests
        import yaml
        import selenium
        import plotly
        from bs4 import BeautifulSoup
        logger.info("✅ All dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/version', timeout=5)
        if response.status_code == 200:
            logger.info("✅ Ollama service is running")
            return True
        else:
            logger.error("❌ Ollama service is not responding")
            return False
    except Exception as e:
        logger.error(f"❌ Cannot connect to Ollama: {e}")
        return False

def run_full_automation(website_url: str):
    """
    Run complete automation workflow:
    URL -> Scrape HTML -> AI Analysis -> BDD Generation -> Test Creation -> Test Execution -> Report
    """
    logger.info("🚀 Starting FULL AUTOMATION workflow")
    logger.info(f"🎯 Target website: {website_url}")
    
    try:
        # Step 1: Web Scraping
        logger.info("📋 Step 1/6: Web Scraping...")
        from src.scraper.web_scraper import WebScraper
        
        scraper = WebScraper()
        scraping_results = scraper.scrape_website(website_url)
        logger.info(f"✅ Scraping completed: {len(scraping_results.links)} links, {len(scraping_results.buttons)} buttons found")
        
        # Step 2: AI Analysis  
        logger.info("🤖 Step 2/6: AI Analysis...")
        from src.ai.ai_client import AIClient
        
        ai_client = AIClient()
        ai_client.set_model("llama3:latest")
        
        # Create simple HTML summary for AI
        html_summary = f"""
        Website: {website_url}
        Title: {scraping_results.title or 'Unknown'}
        Links found: {len(scraping_results.links)}
        Buttons found: {len(scraping_results.buttons)}
        Forms found: {len(scraping_results.forms)}
        
        Sample elements:
        - Links: {[link.get('text', '')[:50] for link in scraping_results.links[:5]]}
        - Buttons: {[btn.get('text', '')[:50] for btn in scraping_results.buttons[:5]]}
        """
        
        ai_analysis = ai_client.analyze_html(html_summary)
        logger.info("✅ AI analysis completed")
        
        # Step 3: BDD Generation
        logger.info("📝 Step 3/6: BDD Test Scenarios Generation...")
        from src.bdd.bdd_generator import BDDGenerator
        
        bdd_generator = BDDGenerator()
        bdd_scenarios = bdd_generator.generate_bdd_from_analysis(ai_analysis, scraping_results)
        logger.info(f"✅ Generated {len(bdd_scenarios)} BDD scenarios")
        
        # Step 4: Test Code Generation
        logger.info("⚙️ Step 4/6: Test Code Generation...")
        from src.automation.test_generator import TestGenerator
        
        test_generator = TestGenerator()
        test_code = test_generator.generate_test_code(scraping_results, bdd_scenarios, website_url)
        logger.info("✅ Test code generated")
        
        # Step 5: Test Execution
        logger.info("🧪 Step 5/6: Running Tests...")
        
        # Run pytest and capture results
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/generated/test_website.py', 
            '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        # Parse test results
        test_results = []
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if '::' in line and ('PASSED' in line or 'FAILED' in line or 'SKIPPED' in line):
                    parts = line.split('::')
                    if len(parts) >= 2:
                        test_name = parts[1].split()[0]
                        status = 'passed' if 'PASSED' in line else ('failed' if 'FAILED' in line else 'skipped')
                        test_results.append({
                            'name': test_name,
                            'status': status,
                            'duration': 2.5  # Approximate duration
                        })
        
        passed = len([t for t in test_results if t['status'] == 'passed'])
        failed = len([t for t in test_results if t['status'] == 'failed'])
        skipped = len([t for t in test_results if t['status'] == 'skipped'])
        
        logger.info(f"✅ Tests completed: {passed} passed, {failed} failed, {skipped} skipped")
        
        # Step 6: Report Generation
        logger.info("📊 Step 6/6: Generating Comprehensive Report...")
        from src.reporting.report_generator import ReportGenerator
        
        report_generator = ReportGenerator()
        
        # Prepare report data
        report_data = {
            'test_results': test_results,
            'website_url': website_url,
            'scraping_results': scraping_results,
            'ai_analysis': ai_analysis,
            'bdd_scenarios': bdd_scenarios,
            'execution_stats': {
                'total_tests': len(test_results),
                'passed_tests': passed,
                'failed_tests': failed,
                'skipped_tests': skipped
            },
            'performance_metrics': {},
            'timestamp': datetime.now().isoformat(),
            'duration': 60.0  # Approximate total duration
        }
        
        # Generate reports
        report_paths = report_generator.generate_comprehensive_report(report_data)
        
        # Final summary
        logger.info("🎉 AUTOMATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"🎯 Website tested: {website_url}")
        logger.info(f"📊 Test results: {passed} passed, {failed} failed, {skipped} skipped")
        logger.info(f"📁 Reports generated:")
        for format_type, path in report_paths.items():
            logger.info(f"   - {format_type.upper()}: {path}")
        logger.info("=" * 60)
        
        # Check screenshots
        screenshot_dir = Path("reports/screenshots")
        if screenshot_dir.exists():
            screenshots = list(screenshot_dir.glob("*.png"))
            logger.info(f"📸 Screenshots captured: {len(screenshots)}")
            for shot in screenshots:
                logger.info(f"   - {shot.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Automation failed: {e}")
        return False

def run_quick_test(website_url: str):
    """Run quick test without AI analysis"""
    logger.info("⚡ Starting QUICK TEST workflow")
    
    try:
        from src.automation.test_generator import TestGenerator
        from src.reporting.report_generator import ReportGenerator
        
        # Simple scraping
        from src.scraper.web_scraper import WebScraper
        scraper = WebScraper()
        scraping_results = scraper.scrape_website(website_url)
        
        # Generate simple tests
        test_generator = TestGenerator()
        test_generator.generate_test_code(scraping_results, [], website_url)
        
        # Run tests
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/generated/test_website.py', 
            '-v'
        ], capture_output=True, text=True)
        
        logger.info("✅ Quick test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Quick test failed: {e}")
        return False

def list_available_models():
    """List available AI models"""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = response.json().get('models', [])
            logger.info("🤖 Available AI models:")
            for model in models:
                logger.info(f"   - {model['name']}")
        else:
            logger.error("❌ Cannot fetch models from Ollama")
    except Exception as e:
        logger.error(f"❌ Error listing models: {e}")

def main():
    """Main entry point"""
    print("    ╔══════════════════════════════════════════════════════════════╗")
    print("    ║                                                              ║")
    print("    ║        🤖 AI Test Automation Assistant 🤖                    ║")
    print("    ║                                                              ║")
    print("    ║     Lokal AI ile Web Sitesi Otomatik Test Üretimi           ║")
    print("    ║                                                              ║")
    print("    ╚══════════════════════════════════════════════════════════════╝")
    print()
    
    parser = argparse.ArgumentParser(
        description="AI-powered web testing automation with local AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --url https://example.com                    # Tam otomatik test süreci
  python main.py --url https://example.com --quick           # Hızlı test (AI olmadan)
  python main.py --list-models                               # Mevcut AI modellerini listele
  
Tam otomatik süreç:
  1. Web sitesi HTML kodlarını çıkarır
  2. AI modeli ile analiz eder
  3. BDD test senaryoları oluşturur
  4. Otomatik test kodları üretir
  5. Testleri çalıştırır
  6. Detaylı rapor oluşturur
        """
    )
    
    parser.add_argument(
        "--url", 
        type=str, 
        help="Test edilecek web sitesi URL'i (örn: https://example.com)"
    )
    
    parser.add_argument(
        "--quick", 
        action="store_true", 
        help="Hızlı test modu (AI analizi olmadan)"
    )
    
    parser.add_argument(
        "--list-models", 
        action="store_true", 
        help="Mevcut AI modellerini listele"
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if not check_dependencies():
        print("❌ Lütfen eksik bağımlılıkları yükleyin: pip install -r requirements.txt")
        sys.exit(1)
    
    if args.list_models:
        list_available_models()
        return
    
    if not args.url:
        print("❌ Web sitesi URL'i gerekli. Kullanım: python main.py --url https://example.com")
        parser.print_help()
        sys.exit(1)
    
    # Validate URL
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url
    
    logger.info(f"🎯 Target URL: {args.url}")
    
    if args.quick:
        success = run_quick_test(args.url)
    else:
        # Check Ollama for full automation
        if not check_ollama_service():
            print("❌ Ollama servisi çalışmıyor. Tam otomatik mod için Ollama gerekli.")
            print("   Hızlı test için: python main.py --url {} --quick".format(args.url))
            sys.exit(1)
        
        success = run_full_automation(args.url)
    
    if success:
        print("\n🎉 İşlem başarıyla tamamlandı!")
        print("📁 Raporları kontrol edin: reports/automation_report.html")
    else:
        print("\n❌ İşlem başarısız oldu. Logları kontrol edin.")
        sys.exit(1)

if __name__ == "__main__":
    main() 