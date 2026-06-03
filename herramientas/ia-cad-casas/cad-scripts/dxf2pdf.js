// dxf2pdf.js
// Script de QCAD para exportar un archivo DXF a PDF en modo headless

include("scripts/simple.js");
include("scripts/File/Print/Print.js");

function main() {
    var inputPath = "";
    var outputPath = "";

    // Parsear argumentos pasados al script
    // Ejemplo de llamada: qcad -no-gui -platform offscreen -autostart dxf2pdf.js -input input.dxf -output output.pdf
    // 'args' es una variable global en QCAD que contiene los argumentos de línea de comando.
    for (var i = 0; i < args.length; i++) {
        if (args[i] === "-input" && i + 1 < args.length) {
            inputPath = args[i + 1];
        }
        if (args[i] === "-output" && i + 1 < args.length) {
            outputPath = args[i + 1];
        }
    }

    if (!inputPath || !outputPath) {
        print("Error: Se requiere especificar -input <archivo.dxf> y -output <archivo.pdf>");
        return;
    }

    print("QCAD: Cargando archivo DXF: " + inputPath);

    // 1. Crear documento e interfaz
    var doc = createOffScreenDocument();
    var di = new RDocumentInterface(doc);

    // 2. Importar el archivo CAD
    var status = di.importFile(inputPath);
    if (status !== RDocumentInterface.IoErrorNoError) {
        print("Error: No se pudo abrir o importar el archivo DXF. Código de error: " + status);
        return;
    }

    print("QCAD: Archivo cargado con éxito. Configurando página y escena...");

    // 3. Crear escena y vista para calcular escala
    var scene = new RGraphicsSceneQt(di);
    var view = new RGraphicsViewImage();
    view.setScene(scene);

    // 4. Inicializar la clase Print
    var printTool = new Print(undefined, doc, view);

    // 5. Configurar tamaño de papel (A4 Landscape)
    doc.setVariable("PageSettings/PaperWidth", 297);  // Horizontal
    doc.setVariable("PageSettings/PaperHeight", 210); // Vertical
    doc.setVariable("PageSettings/PageOrientation", "Landscape");
    doc.setVariable("PageSettings/PaperUnit", RS.Millimeter);
    
    // Auto-ajustar el dibujo al papel y centrar (métodos estáticos de la clase Print)
    Print.autoFitDrawing(di, false);
    Print.autoCenter(di);

    print("QCAD: Exportando a PDF: " + outputPath);
    
    // 6. Exportar
    printTool.print(outputPath);
    print("QCAD: Exportación finalizada con éxito.");
}

if (typeof(including) == 'undefined' || including === false) {
    main();
}
