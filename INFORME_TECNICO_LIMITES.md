# Informe Técnico: Limitaciones de Infraestructura AWS y Solución Alternativa

## 1. Resumen Ejecutivo

Este proyecto implementa una solución completa para la generación de activos digitales utilizando IA Generativa ("GIA: Mugen"). Durante el desarrollo, se identificaron **restricciones críticas de cuota operativa** en la Capa Gratuita (Free Tier) de AWS Bedrock, las cuales impidieron el uso continuo del servicio.

Para garantizar la entregabilidad y funcionalidad del proyecto, se proporcionan dos versiones de la aplicación:

1.  **Versión Principal (BYOK):** Lista para producción, requiere credenciales propias de AWS (del evaluador).
2.  **Versión Alternativa (OpenRouter):** Solución de respaldo funcional que utiliza modelos externos.

## 2. Diagnóstico de Incidencias en AWS Bedrock

Durante las pruebas de integración con Amazon Bedrock (modelos `amazon.titan-image-generator-v2:0` y `anthropic.claude-3-sonnet`), **se logró generar con éxito un lote inicial de aproximadamente 10 imágenes**.

Posteriormente, y debido al consumo acumulado de este testing inicial, la Capa Gratuita alcanzó su límite operativo duro, bloqueando sistemáticamente todas las peticiones subsiguientes con los siguientes errores:

- **Error:** `ThrottlingException`
- **Detalle:** `Too many requests, please wait before trying again.`
- **Error Crítico:** `DailyTokenLimitExceeded`
- **Mensaje de Consola:** "Too many tokens per day".

### Acciones de Mitigación Intentadas:

1.  **Cambio de Región:** Se migró la infraestructura de `us-east-1` (N. Virginia) a `us-west-2` (Oregon) y se auditaron regiones globales (Europa/Asia). Resultado: Bloqueo geográfico o de cuota idéntico.
2.  **Estrategia de Reintentos:** Se implementó lógica de _Exponential Backoff_ con hasta 12 reintentos. Resultado: Los límites son de tipo "Hard Limit" (cuota dura), no solucionables con esperas breves.
3.  **Auditoría de Permisos:** Se verificó la política `AmazonBedrockFullAccess`. Resultado: Los permisos IAM son correctos, confirmando que el bloqueo es a nivel de _Service Quota_ de la cuenta de laboratorio.

## 3. Solución Implementada: Modelo "Bring Your Own Key" (BYOK)

Para superar estas limitaciones de la Capa Gratuita y permitir una evaluación justa de la arquitectura propuesta, la aplicación principal (`app_gia_bedrock.py`) ha sido refactorizada para operar en modo **BYOK**.

- **Funcionamiento:** La aplicación no depende de credenciales hardcodeadas o del entorno local limitado.
- **Uso:** El evaluador puede ingresar sus propias credenciales de AWS (Access Key / Secret Key) con permisos estándar de Bedrock directamente en el panel lateral.
- **Ventaja:** Permite probar la potencia real de los modelos Titan V2 y Stable Image Core sin las restricciones de la cuenta educativa.

## 4. Alternativa de Respaldo: OpenRouter

Como medida de contingencia adicional, se incluye una versión (`app_gia_openrouter_demo.py`) conectada a **OpenRouter**.
Esta versión demuestra la funcionalidad de la aplicación (generación de imagen + edición de texto) utilizando modelos equivalentes (GPT-5 Image Mini / Nvidia Nemotron) fuera de la infraestructura de AWS, asegurando que siempre haya una demo funcionable disponible.

---

**Conclusión:** La arquitectura de software es robusta y funcional. Las limitaciones encontradas son exclusivamente atribuibles a las restricciones de cuota de la Capa Gratuita de AWS Bedrock.
