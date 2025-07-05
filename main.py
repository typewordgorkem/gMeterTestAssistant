#!/usr/bin/env python3
"""
AI Test Automation Assistant
Main entry point for the application
"""

import argparse
import asyncio
import sys
from pathlib import Path
from loguru import logger
import yaml
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.orchestrator.main_orchestrator import MainOrchestrator, ExecutionConfig


def setup_logging():
    """Setup logging configuration"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "logs/automation.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )


def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🤖 AI Test Automation Assistant 🤖                    ║
    ║                                                              ║
    ║     Lokal AI ile Web Sitesi Otomatik Test Üretimi           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="AI Test Automation Assistant - Lokal AI ile otomatik test üretimi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py --url https://example.com --ai-model llama2
  python main.py --url https://example.com --ai-model mistral --headless
  python main.py --quick-test --url https://example.com
  python main.py --list-models
        """
    )
    
    # Main arguments
    parser.add_argument(
        "--url",
        type=str,
        help="Test edilecek web sitesinin URL'si"
    )
    
    parser.add_argument(
        "--ai-model",
        type=str,
        default="llama2",
        help="Kullanılacak AI model adı (default: llama2)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Çıktı dosyalarının kaydedileceği klasör (default: reports)"
    )
    
    # Execution options
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Tarayıcıyı görünmez modda çalıştır"
    )
    
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Testleri paralel olarak çalıştırma"
    )
    
    parser.add_argument(
        "--no-reports",
        action="store_true",
        help="Rapor üretme"
    )
    
    parser.add_argument(
        "--no-artifacts",
        action="store_true",
        help="Artifact dosyalarını kaydetme"
    )
    
    # Utility options
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Hızlı test çalıştır (sadece scraping ve AI analizi)"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Mevcut AI modellerini listele"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Konfigürasyon dosyasını doğrula"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Konfigürasyon dosyası yolu (default: config/config.yaml)"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Detaylı log çıktısı"
    )
    
    return parser


async def run_full_automation(args):
    """Run full automation workflow"""
    logger.info("Starting full automation workflow")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator(args.config)
    
    # Create execution config
    execution_config = ExecutionConfig(
        url=args.url,
        ai_model=args.ai_model,
        output_dir=args.output_dir,
        headless=args.headless,
        parallel_tests=not args.no_parallel,
        generate_reports=not args.no_reports,
        save_artifacts=not args.no_artifacts
    )
    
    # Execute automation
    result = await orchestrator.execute_full_automation(execution_config)
    
    # Print results
    if result.success:
        logger.info("✅ Automation completed successfully!")
        print(f"\n🎉 Automation completed in {result.execution_time:.2f} seconds")
        print(f"📊 Reports generated: {len(result.reports)}")
        print(f"🗂️  Artifacts saved: {result.artifacts_saved}")
        
        if result.reports:
            print("\n📋 Generated Reports:")
            for report_type, report_path in result.reports.items():
                print(f"  - {report_type.upper()}: {report_path}")
    else:
        logger.error("❌ Automation failed!")
        print(f"\n💥 Automation failed: {result.error_message}")
        sys.exit(1)


async def run_quick_test(args):
    """Run quick test"""
    logger.info("Starting quick test")
    
    # Initialize orchestrator
    orchestrator = MainOrchestrator(args.config)
    
    # Run quick test
    result = await orchestrator.quick_test(args.url, args.ai_model)
    
    # Print results
    if result['success']:
        print(f"\n✅ Quick test completed for: {result['url']}")
        print(f"📄 Page title: {result['title']}")
        print(f"📝 Forms found: {result['forms_count']}")
        print(f"🔗 Links found: {result['links_count']}")
        print(f"🔘 Buttons found: {result['buttons_count']}")
        print(f"🤖 AI model used: {result['ai_model']}")
        print(f"\n📋 Analysis preview:\n{result['analysis_preview']}...")
    else:
        logger.error("❌ Quick test failed!")
        print(f"\n💥 Quick test failed: {result['error']}")
        sys.exit(1)


def list_models(args):
    """List available AI models"""
    logger.info("Listing available AI models")
    
    try:
        # Initialize orchestrator
        orchestrator = MainOrchestrator(args.config)
        
        # Get available models
        models = orchestrator.get_available_ai_models()
        
        if models:
            print("\n🤖 Available AI Models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
        else:
            print("\n⚠️  No AI models found. Make sure your AI service is running.")
            
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        print(f"\n💥 Error listing models: {e}")
        sys.exit(1)


def validate_config(args):
    """Validate configuration"""
    logger.info("Validating configuration")
    
    try:
        # Initialize orchestrator
        orchestrator = MainOrchestrator(args.config)
        
        # Validate config
        if orchestrator.validate_config():
            print("\n✅ Configuration is valid!")
        else:
            print("\n❌ Configuration validation failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error validating config: {e}")
        print(f"\n💥 Error validating config: {e}")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import selenium
        import requests
        import bs4  # beautifulsoup4 imports as bs4
        import yaml
        import loguru
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False


async def main():
    """Main function"""
    print_banner()
    
    # Setup logging
    setup_logging()
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Set verbose logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stdout, level="DEBUG")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Handle different commands
    try:
        if args.list_models:
            list_models(args)
        elif args.validate_config:
            validate_config(args)
        elif args.quick_test:
            if not args.url:
                logger.error("URL is required for quick test")
                print("❌ URL is required for quick test. Use --url parameter.")
                sys.exit(1)
            await run_quick_test(args)
        else:
            # Full automation
            if not args.url:
                logger.error("URL is required for full automation")
                print("❌ URL is required. Use --url parameter.")
                parser.print_help()
                sys.exit(1)
            await run_full_automation(args)
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        print("\n👋 Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Run main function
    asyncio.run(main()) 