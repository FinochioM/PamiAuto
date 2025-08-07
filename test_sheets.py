from browser_automation import BrowserAutomation
from logger import AutomationLogger
import json
from config import *

def test_google_sheets_connection():
    print("=== TESTING GOOGLE SHEETS CONNECTION ===")
    print(f"Date range filter: {DATE_RANGE_START} to {DATE_RANGE_END}")
    
    # Create logger and automation instance
    logger = AutomationLogger()
    automation = BrowserAutomation(logger)
    
    try:
        # Test reading data from Google Sheets
        print("Conectando a Google Sheets...")
        excel_data = automation.read_excel_data()
        
        print(f"\n✅ Conexión exitosa!")
        print(f"Total de casos sin procesar: {len(excel_data)}")
        print(f"Casos ya procesados anteriormente: {len(automation.already_processed_cases)}")
        
        # Show column names
        if excel_data:
            print(f"\nColumnas disponibles: {list(excel_data[0].keys())}")
            
            # Show first few records
            print(f"\nPrimeros 3 registros sin procesar:")
            for i, record in enumerate(excel_data[:3]):
                print(f"  Registro {i+1}:")
                for key, value in record.items():
                    print(f"    {key}: {value}")
                print()
        
        # Show already processed cases
        if automation.already_processed_cases:
            print(f"\nCasos ya procesados:")
            for case in automation.already_processed_cases[:5]:  # Show first 5
                print(f"  - NDO {case['NDO']} (COD {case['COD']}) - {case['APE']} {case['NOM']}")
        
        print(f"\nTest completado exitosamente!")
        return True
        
    except Exception as e:
        print(f"\nError en el test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_sheets_connection()
    if success:
        print("\nGoogle Sheets integration working correctly!")
    else:
        print("\nGoogle Sheets integration needs fixing.")