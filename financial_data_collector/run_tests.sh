#!/bin/bash
# Module 1: Comprehensive Test Runner
# Easy interface for running production readiness tests

set -e

echo "🚀 Module 1: Financial Data Collector - Test Runner"
echo "=================================================="

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Test Options:"
    echo "  full         Run complete test suite (default)"
    echo "  quick        Run quick tests (skip performance)"
    echo "  collectors   Test only data collectors"
    echo "  verbose      Run with detailed logging"
    echo "  critical     Run only critical tests"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh full      # Complete production test"
    echo "  ./run_tests.sh quick     # Fast test for development"
    echo "  ./run_tests.sh verbose   # Detailed test output"
    echo ""
}

# Function to check Python environment
check_environment() {
    echo "🔍 Checking Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 not found"
        exit 1
    fi
    
    echo "✅ Python 3: $(python3 --version)"
    
    # Check for essential packages
    python3 -c "import pandas, yaml" 2>/dev/null || {
        echo "❌ Missing required packages (pandas, yaml)"
        echo "   Run: pip install pandas pyyaml"
        exit 1
    }
    
    echo "✅ Essential packages available"
}

# Function to run tests
run_tests() {
    local test_type="$1"
    
    echo ""
    echo "🧪 Running $test_type tests..."
    echo "Started: $(date)"
    echo ""
    
    case $test_type in
        "full")
            python3 test_module_1_comprehensive.py
            ;;
        "quick")
            python3 test_module_1_comprehensive.py --quick
            ;;
        "collectors")
            python3 test_module_1_comprehensive.py --collectors-only
            ;;
        "verbose")
            python3 test_module_1_comprehensive.py --verbose
            ;;
        "critical")
            python3 test_module_1_comprehensive.py --quick --collectors-only
            ;;
        *)
            echo "❌ Unknown test type: $test_type"
            show_usage
            exit 1
            ;;
    esac
}

# Function to show test results summary
show_summary() {
    echo ""
    echo "📋 Test Summary"
    echo "==============="
    
    # Find the most recent log file
    latest_log=$(ls -t test_results_*.log 2>/dev/null | head -1)
    
    if [[ -f "$latest_log" ]]; then
        echo "📁 Detailed log: $latest_log"
        echo ""
        echo "📊 Quick Stats:"
        grep -E "(Tests Run|Passed|Failed|Success Rate)" "$latest_log" 2>/dev/null || echo "   Log analysis unavailable"
    else
        echo "   No test log found"
    fi
    
    echo ""
    echo "🎯 Next Steps:"
    echo "   • Review test results above"
    echo "   • Fix any critical failures"
    echo "   • Run production deployment when ready"
}

# Main execution
main() {
    local test_type="${1:-full}"
    
    # Special case for help
    if [[ "$test_type" == "-h" ]] || [[ "$test_type" == "--help" ]] || [[ "$test_type" == "help" ]]; then
        show_usage
        exit 0
    fi
    
    # Navigate to the correct directory
    cd "$(dirname "$0")"
    
    # Run pre-checks
    check_environment
    
    # Execute tests
    run_tests "$test_type"
    
    # Show summary
    show_summary
}

# Execute main function with all arguments
main "$@" 