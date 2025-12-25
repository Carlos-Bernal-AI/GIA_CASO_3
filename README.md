# GIA: Mugen - Suite Creativa de IA

**Entrega Final - Caso Práctico Unidad 3**

**GIA: Mugen** es una plataforma avanzada de generación de activos digitales que integra inteligencia artificial multimodal para potenciar flujos de trabajo creativos.

---

## 🌟 Aplicación Principal: GIA Mugen (Bedrock Edition)

**Archivo:** `app_gia_bedrock.py`

Esta es la **solución oficial y definitiva** del proyecto. Implementa una arquitectura robusta sobre **Amazon Bedrock** para ofrecer una suite completa:

### Características Clave

- **🎨 Generación de Imágenes Multi-Modelo**:
  - **Amazon Titan Image Generator v2**: Para generaciones realistas y precisas.
  - **Stable Image Core**: Para arte estilizado y creatividad visual.
- **✨ Mejora de Prompts con IA**:
  - Funcionalidad integrada que utiliza **Claude 3 Sonnet** para convertir ideas simples en prompts de ingeniería detallados automáticamente.
- **📝 Editor de Texto Inteligente**:
  - Panel dedicado para redacción, corrección y expansión de textos con Claude 3.
- **🔑 Modo BYOK (Bring Your Own Key)**:
  - Diseñada para entornos de evaluación profesional. Permite ingresar credenciales propias de AWS (Access Key / Secret / Session Token) directamente en la interfaz.
  - _Nota: Esto soluciona las limitaciones de cuota "DailyTokenLimit" detectadas en las cuentas de Capa Gratuita._

### Cómo Evaluar (Recomendado)

Ejecute la aplicación y configure sus credenciales en el panel lateral "Configuración AWS":

```bash
streamlit run app_gia_bedrock.py
```

---

## �️ Alternativa de Respaldo: OpenRouter Edition

**Archivo:** `app_gia_openrouter_demo.py`

Debido a que la cuota operativa de la Capa Gratuita de AWS se agotó tras las pruebas iniciales, se proporciona esta **versión de contingencia**.

- **Propósito**: Demostrar la funcionalidad de la interfaz y la lógica de validación si no se dispone de credenciales AWS Bedrock activas.
- **Tecnología**: Conecta a la API de OpenRouter utilizando modelos equivalentes (GPT-5 Image Mini / Nvidia Nemotron).

### Ejecución de Respaldo

```bash
streamlit run app_gia_openrouter_demo.py
```

---

## 📄 Notas Técnicas

Consulte el archivo `INFORME_TECNICO_LIMITES.md` para un desglose detallado sobre los desafíos de infraestructura encontrados en AWS Free Tier y cómo esta entrega los mitiga.

---

© 2025 Proyecto GIA Mugen
