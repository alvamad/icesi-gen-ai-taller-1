## 1. Selección y Justificación del Modelo de IA  

La opción más adecuada para EcoMarket es una **solución híbrida**, en la que la automatización mediante un **LLM grande más económico (por ejemplo, GPT-3.5 o GPT-4 mini) con RAG** atienda el **80% de las consultas repetitivas** (estado del pedido, devoluciones, características del producto), reduciendo tiempos de espera y liberando carga operativa, mientras que el **20% de los casos más complejos** se aborde con un **LLM grande más robusto (por ejemplo, GPT-4)** dentro de un esquema de *human in the loop*, garantizando empatía, flexibilidad y un trato personalizado.  

Para habilitar esta diferenciación, en la **arquitectura propuesta** se incorpora un módulo de **“Clasificación de intenciones / Orquestador”**, que recibe la entrada de las consultas (chat, email o redes sociales) y determina automáticamente si son repetitivas o complejas. Este proceso se realiza en varias etapas: primero, el sistema analiza la consulta con un preprocesamiento inicial que extrae palabras clave relevantes (como “pedido”, “devolución” o “SKU”) y detecta datos estructurados, como identificadores de pedidos. Luego, un clasificador de intenciones entrenado con ejemplos históricos de EcoMarket asigna una probabilidad a cada tipo de consulta, diferenciando las de carácter transaccional repetitivo (ejemplo: estado de pedido, devoluciones) de aquellas más abiertas y complejas (ejemplo: quejas, sugerencias, problemas técnicos). Además, se aplican umbrales de confianza para decidir la ruta adecuada y reglas heurísticas que refuerzan la clasificación, como identificar expresiones negativas o términos sensibles que obligan a tratar el caso como complejo. Finalmente, el sistema se enriquece con retroalimentación continua, ya que los errores de clasificación y los casos corregidos manualmente por agentes humanos sirven como nuevos ejemplos de entrenamiento para mejorar la precisión con el tiempo.  

### Rutas definidas  
- **Consultas repetitivas (80%)**: resueltas por un **LLM grande más económico (GPT-3.5 o GPT-4 mini) con RAG y conectado a Tools/APIs**, lo que asegura precisión en información transaccional como pedidos y devoluciones.  
- **Consultas complejas (20%)**: gestionadas por un **LLM grande más robusto (GPT-4) con RAG**, priorizando fluidez y empatía, con la opción de escalar a un agente humano en caso de incertidumbre o riesgo reputacional.  

**Arquitectura del modelo:** el diseño híbrido combina eficiencia y bajo costo en lo transaccional con un modelo económico, y flexibilidad conversacional en lo complejo con un modelo avanzado. El **orquestador** actúa como puente que dirige cada interacción a la solución correspondiente, mientras que la capa de integración a **APIs de EcoMarket** garantiza acceso a información en tiempo real sin riesgo de alucinaciones.  

**Costo:** esta solución es más eficiente que usar únicamente un LLM robusto, ya que el 80% de los casos se resuelven con un modelo más económico, reservando el modelo avanzado solo para el 20% complejo, optimizando así el gasto en cómputo y licencias.  

**Escalabilidad:** el enfoque modular permite crecer en volumen y canales (chat, correo, redes sociales) sin reentrenar desde cero. Basta con actualizar la base de conocimiento de RAG y ajustar la orquestación, lo que facilita la adaptación al crecimiento de EcoMarket.  

**Facilidad de integración:** al conectarse mediante **Tools/APIs** al catálogo de productos, sistemas de pedidos y envíos, la solución se integra con las plataformas existentes de EcoMarket, reduciendo fricción en la implementación y garantizando que las respuestas estén alineadas con la información oficial de la empresa.  

En conclusión, la **solución híbrida** ofrece un equilibrio óptimo entre **precisión, empatía, costo y escalabilidad**, apoyándose en la clasificación inicial de consultas para aprovechar lo mejor de ambos modelos y asegurar una atención al cliente más rápida, confiable y humana.  

## 2. Evaluación de Fortalezas, Limitaciones y Riesgos Éticos  

### **Fortalezas**  
La solución híbrida de EcoMarket permite una **reducción significativa del tiempo de respuesta**, resolviendo de inmediato el **80% de las consultas repetitivas** mediante un **LLM grande más económico (por ejemplo, GPT-3.5 o GPT-4 mini) con RAG** y conectado a las bases de datos de pedidos, devoluciones y catálogo. También ofrece **disponibilidad 24/7**, asegurando soporte constante en múltiples canales, y aporta **escalabilidad**, ya que puede atender miles de interacciones sin necesidad de ampliar proporcionalmente el equipo humano. Además, mejora la **consistencia en las respuestas**, alineando cada interacción con la información oficial de la empresa y reduciendo variaciones de criterio. Finalmente, libera al personal de tareas rutinarias, permitiendo que los agentes se concentren en el **20% de los casos complejos**, donde la empatía y el juicio humano aportan mayor valor.  

### **Limitaciones**  
La efectividad de la solución depende en gran medida de la **calidad de los datos**; si la información de pedidos, devoluciones o productos está desactualizada o es errónea, el modelo transmitirá esos errores. Asimismo, incluso los LLM grandes más económicos pueden presentar **limitaciones en conversaciones largas o altamente personalizadas**, perdiendo parte del contexto. Otro desafío es la necesidad de un **mantenimiento constante** de la base de conocimiento (RAG) y las integraciones con APIs para reflejar cambios en políticas, inventario y procesos. El **costo operativo** sigue siendo un factor, especialmente en el 20% de casos donde se recurre a un **LLM robusto como GPT-4**, que tiene mayor consumo de recursos. Finalmente, se requiere gestionar una **curva de adopción interna**, ya que los agentes deben capacitarse para trabajar en conjunto con la IA y comprender cuándo intervenir en el esquema de *human in the loop*.  

### **Riesgos Éticos**  
Uno de los riesgos más relevantes son las **alucinaciones del modelo**, que pueden llevar a inventar información en ausencia de contexto. Esto debe mitigarse con controles de confianza, reglas estrictas y escalado a humano en casos inciertos. También está el riesgo de **sesgos en el lenguaje**, ya que el modelo podría replicar patrones discriminatorios presentes en sus datos de entrenamiento y dar respuestas diferenciadas según el perfil del cliente. La **privacidad de los datos** es otro aspecto fundamental: se debe anonimizar información de identificación personal y cumplir con normativas de protección como GDPR o CCPA para garantizar seguridad. Además, existe un **impacto laboral** que no debe ignorarse; la automatización puede generar preocupación en los agentes de soporte, por lo que la estrategia debe enfocarse en **empoderarlos**, reduciendo su carga repetitiva y dándoles espacio para aportar mayor valor en casos complejos. Finalmente, es indispensable garantizar la **transparencia con los clientes**, dejando claro cuándo interactúan con un bot y cuándo con un humano, para mantener la confianza en la marca.  

# 3. Observaciones para el Prompt implementado

En general, para la consecución del prompt que se escogió para este ejercicio, 
podríamos plantear diferentes evoluciones pero con ciertas limitaciones:

 - “Dime el estado del pedido 12345.” Este es demasiado simple, porque no define el rol del modelo ni le indica cómo debe responder. Además, no asegura que use solo la información disponible y no da instrucciones en caso de que falten datos o haya retrasos.
 - “Eres un agente de servicio al cliente. Usa la información que tengas para responder sobre pedidos y mantén un tono cordial.” Este ya mejora un poco, porque define un rol y pide cortesía. Sin embargo, sigue siendo limitado: no dice qué hacer si falta el número de pedido ni cómo manejar retrasos o dar detalles extra como la fecha de entrega.
 - “Actúa como agente de EcoMarket. Responde en español neutro y cordial usando solo la información del contexto. Si falta el número de pedido, pide al cliente que lo comparta. Si el pedido está retrasado, ofrece una disculpa.” Aquí ya se incorporan reglas más claras, pero todavía falta indicar acciones concretas ante retrasos y añadir información como estimaciones de entrega o enlaces de rastreo.

 Pero se decidió finalmente por tres prompts diferentes, uno de contexto/reglas, otro para el estado orden y otro para las peticiones de retorno. Por ejemplo el de contexto:

 "Eres un agente de servicio al cliente de EcoMarket: amable, claro, conciso y empático.
Reglas:
- Usa solo la información provista en el contexto (pedidos y políticas).
- Si falta información, pide amablemente el dato necesario y no inventes.
- Cuando haya retraso, ofrece una disculpa breve y una acción concreta.
- Incluye estimación de entrega y enlace de rastreo cuando corresponda.
- Responde en español neutro y con tono profesional y cordial."

Contiene todas las reglas que se necesitan para el contexto inicial, órdenes claras y directas para que pueda sacar la información de la base que se le pasa después, incluye forma de responder, tonos, y demás indicaciones.

Los otros dos prompts que usaron para RAG se pueden encontrar en [returns_prompt.txt](prompts/returns_prompt.txt) y [order_status_prompt](prompts/order_status_prompt.txt)

Como se puede observar son prompts que tienen objetivo, contexto, inputs, reglas, y demás contenido que permite al LLM tomar decisiones adecuadas y acertadas para responder con el mayor grado de acercamiento posible a la intención del usuario.

Como ejemplo de interacción tenemos la siguiente captura:
![alt text](resultado.png)