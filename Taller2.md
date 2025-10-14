# Proyecto EcoMarket – Implementación de Sistema RAG

## Fase 1: Selección de Componentes Clave del Sistema RAG

### Modelo de Embeddings: multilingual-e5-large

**Precisión (español):**  
`multilingual-e5-large` es un modelo avanzado de **recuperación semántica**, desarrollado por *Intfloat* y disponible en Hugging Face. Está **entrenado específicamente para tareas de búsqueda y preguntas y respuestas (QA)**, lo que le permite comprender con gran precisión las consultas de los usuarios y relacionarlas con los fragmentos de texto más relevantes. Su entrenamiento incluye una amplia cantidad de datos en **español**, lo que garantiza un excelente desempeño al procesar textos propios de EcoMarket, como políticas de devolución, catálogos de productos o guías de atención al cliente. Gracias a este enfoque, el modelo puede identificar la información precisa dentro de los documentos de la empresa y ofrecer respuestas coherentes y contextualizadas, **reduciendo así las alucinaciones del modelo generativo y mejorando la fiabilidad del sistema RAG.**

**Costo:**  
Al ser open-source, no tiene costo por uso ni dependencia de APIs externas. Puede ejecutarse on-premise o en la nube, optimizando costos según el volumen de consultas. El modelo tiene **1024 dimensiones**, lo que mantiene un buen equilibrio entre **precisión y eficiencia**, siendo más liviano que otros embeddings de mayor tamaño (como los de OpenAI con 3072 dimensiones). Esto reduce el costo de almacenamiento y acelera la búsqueda vectorial, **incrementando el rendimiento general del sistema**.

**Escalabilidad:**  
Su arquitectura permite procesamiento en **lotes (batch)** y despliegue distribuido en **GPU o CPU con autoescalado**, facilitando atender grandes volúmenes de documentos o consultas simultáneas. Además, mantiene **consistencia entre versiones**, por lo que los índices vectoriales creados con versiones anteriores siguen siendo válidos. Esto evita la necesidad de reindexar cada vez que se actualiza el modelo, garantizando **continuidad operativa**, menor tiempo de mantenimiento y una reducción significativa en **costos de procesamiento y tiempos de respuesta**.

**Integración:**  
Cuenta con soporte directo en librerías como **LangChain**, **LlamaIndex**, **Sentence-Transformers** y **FAISS**, lo que facilita su implementación en pipelines RAG. Su formato de entrada (`query:` y `passage:`) estandariza la generación de embeddings tanto para preguntas como para documentos. Esto permite integrarlo sin fricción con los sistemas de EcoMarket, aprovechando flujos ETL para convertir información en vectores e indexarlos en bases vectoriales como **ChromaDB**, **Pinecone** o **Weaviate**. En conjunto, estos factores garantizan una integración eficiente, escalable y con **recuperaciones semánticas precisas** que fortalecen el rendimiento del sistema RAG.

---

## Fase 2: Creación de la Base de Conocimiento de Documentos

### 1. Identificación de documentos relevantes
Para el caso de **EcoMarket**, se identifican tres tipos de documentos esenciales que contienen la información necesaria para responder con precisión a las consultas de clientes en el sistema de atención:  

- **Política de devoluciones y garantías (PDF):** documento oficial donde se detallan los procedimientos, plazos y condiciones para devoluciones y reclamos.  
- **Catálogo de productos e inventario (Excel o CSV):** contiene la descripción de los productos, precios, disponibilidad y características técnicas.  
- **Preguntas frecuentes (FAQ) (JSON o texto estructurado):** incluye respuestas a consultas comunes sobre métodos de pago, tiempos de envío y seguimiento de pedidos.  

Estos tres tipos de documentos cubren tanto el **componente operativo** (estado de pedidos, inventario, políticas) como el **componente informativo** (guías y atención postventa), garantizando una base de conocimiento **completa, actualizada y coherente** para el modelo RAG. Una **alta calidad y actualización constante de estos documentos** es fundamental, ya que errores o información desactualizada pueden propagarse a las respuestas del modelo, reduciendo la fiabilidad y precisión del sistema.  

---

### 2. Estrategia de segmentación (Chunking)
La segmentación de los documentos en fragmentos o *chunks* es esencial para que el modelo pueda **recuperar la información más relevante sin perder contexto**.  

Para **EcoMarket**, se propone una **estrategia adaptada al tipo de documento**:  

- **PDFs:** segmentación por secciones o temas (“tiempos de devolución”, “condiciones de reembolso”).  
- **Catálogos (CSV):** segmentación por grupos de productos o categorías (“hogar”, “cuidado personal”).  
- **FAQs:** segmentación por pregunta y respuesta, asegurando coherencia y facilidad de interpretación.  

Cada fragmento tendrá entre **250 y 500 tokens**, manteniendo coherencia sin perder precisión. Esta estrategia, centrada en la lógica empresarial de EcoMarket, **mejora la precisión del sistema RAG**, acelera la recuperación de información y reduce el riesgo de respuestas incompletas.

---

### 3. Base de Datos Vectorial

Se evaluaron las principales **bases de datos vectoriales** para seleccionar la más adecuada según **escalabilidad, costo y facilidad de uso**:

| Criterio | Pinecone | Weaviate | ChromaDB |
|-----------|-----------|-----------|-----------|
| Escalabilidad | Alta. Escala automáticamente con millones de vectores y baja latencia (<50 ms). Ideal para entornos productivos. | Alta. Permite clústeres distribuidos y búsqueda híbrida (BM25 + vector). | Media. Adecuado para proyectos pequeños o de desarrollo; limitada en entornos locales. |
| Costo | Pago por almacenamiento y consultas (SaaS). Sin mantenimiento propio. | Puede auto-hospedarse sin costo de licencia, pero requiere infraestructura. | Gratuito (open-source). Ideal para fases iniciales. |
| Facilidad de uso | Muy alta. Integración directa con LangChain y LlamaIndex mediante API key. | Moderada. Requiere configuración de esquemas y GraphQL. | Alta. Instalación rápida y compatibilidad inmediata con LangChain. |

Con base en este análisis, se selecciona **ChromaDB** para las pruebas iniciales del sistema RAG, por su **facilidad de uso, costo cero e integración sencilla**. Al escalar el sistema, se migrará a **Pinecone**, que ofrece **rendimiento empresarial y alta disponibilidad**.

---

### 4. Proceso de indexación
Una vez segmentados los documentos, cada fragmento se transforma en un **vector numérico** usando el modelo **`intfloat/multilingual-e5-large`**, que convierte texto en representaciones semánticas de 1024 dimensiones.  

**Etapas del proceso:**  
1. **Extracción y limpieza:** los documentos se convierten a texto plano eliminando caracteres innecesarios.  
2. **Vectorización:** los fragmentos se procesan con el modelo de embeddings, generando vectores semánticos.  
3. **Carga en la base vectorial:** los vectores y sus metadatos (`tipo_documento`, `categoría`, `fecha_actualización`, `origen`) se almacenan en **ChromaDB** o **Pinecone**.  

Esta estructura facilita las **búsquedas por similitud semántica**, permitiendo construir respuestas **precisas y basadas en información real**, incrementando la eficiencia y confiabilidad del sistema de atención al cliente.

---

## Fase 3: Integración y Ejecución del Código

Durante la ejecución del código y las pruebas del sistema RAG, se evaluó cómo la **calidad de los documentos** y la **estrategia de segmentación** afectan directamente el rendimiento del modelo.  

Se probaron dos configuraciones de embeddings:  
- **`multilingual-e5-large` (Hugging Face):** modelo open-source con buen rendimiento general, pero menor alineación semántica en fragmentos breves y variados.  
- **`text-embedding-3-large` (OpenAI):** modelo más robusto, con mejor comprensión semántica y rendimiento en español.  

Con **`text-embedding-3-large`**, las respuestas mejoraron notablemente porque el modelo capta mejor la **intención en español** y relaciona consultas con fragmentos **heterogéneos** (políticas, productos, FAQs) sin requerir ajustes como los prefijos `query:` o `passage:`. Esto permitió una **recuperación multifuente precisa**, citando correctamente políticas de garantía, datos del catálogo (como el *cepillo de bambú* con precio y stock) y respuestas de las FAQs sobre tiempos de entrega y rastreo.  

El espacio vectorial de GPT, más **denso y robusto**, aumentó la **precisión y el recall** en los resultados top-k, reduciendo respuestas genéricas y alucinaciones. En conclusión, aunque **OpenAI implica mayor costo y dependencia del proveedor**, ofrece un rendimiento más **consistente, contextual y coherente**, garantizando respuestas precisas y de mayor calidad para el sistema RAG de EcoMarket.
