// @category WebReverseLab

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Instruction; // Добавлен импорт
import java.io.FileWriter;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class ExportFunctions extends GhidraScript {

    // Список префиксов MinGW, которые мы считаем системным мусором
    private static final String[] SYSTEM_PREFIXES = {
        "__mingw", "mingw_", "_pei386", "__gcc", "__do_global", 
        "CRTStartup", "_initterm", "__iob", "__set_", "_amsg", 
        "_cexit", "___chkstk", "_config", "_Validate", "_FindPESection",
        "__tmain", "WinMainCRTStartup", "mainCRTStartup", "atexit"
    };

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        String outputPath = "ghidra_output.json";
        if (args.length > 0) {
            outputPath = args[0];
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        
        // Получаем итератор функций
        var functions = functionManager.getFunctions(true);
        
        // Собираем ручной JSON-формат для простоты и скорости без внешних библиотек
        StringBuilder json = new StringBuilder();
        json.append("[\n");

        int maxFunctions = 200;
        int maxAsmLines = 50;
        int count = 0;

        while (functions.hasNext() && count < maxFunctions) {
            Function func = functions.next();
            String funcName = func.getName();
            String funcAddress = func.getEntryPoint().toString();

            // Проверяем, является ли функция системной
            boolean isSystem = false;
            for (String prefix : SYSTEM_PREFIXES) {
                if (funcName.startsWith(prefix) || funcName.contains("CRTStartup")) {
                    isSystem = true;
                    break;
                }
            }

            if (count > 0) {
                json.append(",\n");
            }

            json.append("  {\n");
            json.append("    \"name\": \"").append(funcName).append("\",\n");
            json.append("    \"address\": \"").append(funcAddress).append("\",\n");
            json.append("    \"is_system\": ").append(isSystem).append(",\n");
            json.append("    \"asm\": [");

            // Собираем ASM только для пользовательских функций
            if (!isSystem) {
                var codeUnits = listing.getCodeUnits(func.getBody(), true);
                int asmCount = 0;
                boolean firstAsm = true;

                while (codeUnits.hasNext() && asmCount < maxAsmLines) {
                    CodeUnit cu = codeUnits.next();
                    
                    // ИСПРАВЛЕНО: Проверяем, является ли CodeUnit именно инструкцией процессорного кода
                    if (cu instanceof Instruction) {
                        Instruction instr = (Instruction) cu;
                        
                        if (!firstAsm) {
                            json.append(", ");
                        }
                        
                        String addr = instr.getMinAddress().toString();
                        String mnemonic = instr.getMnemonicString();
                        
                        // Собираем операнды через объект Instruction
                        int numOperands = instr.getNumOperands();
                        List<String> operands = new ArrayList<>();
                        for (int i = 0; i < numOperands; i++) {
                            operands.add(instr.getDefaultOperandRepresentation(i));
                        }
                        String operandsStr = String.join(", ", operands);
                        
                        // Формируем строчку ASM и экранируем кавычки на всякий случай
                        String asmLine = addr + ": " + mnemonic + " " + operandsStr;
                        asmLine = asmLine.replace("\\", "\\\\").replace("\"", "\\\""); 
                        
                        json.append("\"").append(asmLine).append("\"");
                        firstAsm = false;
                        asmCount++;
                    }
                }
            }

            json.append("]\n");
            json.append("  }");
            count++;
        }

        json.append("\n]");

        // Записываем собранную JSON строку в файл
        try (FileWriter file = new FileWriter(new File(outputPath))) {
            file.write(json.toString());
        }

        println("---GHIDRA_DONE---");
    }
}
