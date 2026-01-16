# 🏩 PROYECTO: Odoo 19 CE | Sistema Financiero POS "Multi-Divisa Dinámico" (Vzla)

**Versión del Documento:** 2.0 (High-End Engineering Spec)  
**Objetivo:** Proveer una plataforma de venta minorista que permita **operar comercialmente** en una moneda dura seleccionable (EUR o USD) mientras mantiene la **contabilidad fiscal** en VES, con automatización de tasas BCV y gestión granular de IGTF.

## 1. Arquitectura del Núcleo: "El Pivote Dinámico"

### A. Configuración Maestra de Operación (Operational Settings)

En *Ajustes > Contabilidad > Localización Venezuela*, se desarrollará un selector de campo llamado:

- **Campo:** `Moneda Operativa Principal` (`operational_currency_id`)
- **Opciones:** [ 🇧🇪 Euro ] ó [ 🇺🇸 Dólar ]
- **Efecto del Cambio:** Al cambiar esta selección, el sistema dispara un **"Trigger de Re-configuración Masiva"**:
  1. **Ajuste de Tarifas:** Cambia automáticamente la *Lista de Precios por Defecto* del POS a la moneda seleccionada.
  2. **Ajuste de Visualización:** El POS ahora priorizará la moneda elegida en los totales y recibos.
  3. **Ajuste de Conversión:** La lógica de "Referencia BCV" cambia para usar la tasa de la nueva moneda principal como divisor base.

### B. Base Legal vs. Base Comercial

- **Moneda de la Compañía (Base de Datos):** **VES (Bolívares)**. (Inamovible por ley).
- **Moneda de Transacción:** Dinámica (EUR o USD según el selector anterior).
- *Ingeniería:* El sistema siempre calculará: `Precio Divisa * Tasa BCV = Monto Fiscal VES`.

## 2. Backend: Motor de Inteligencia Cambiaria (Exchange Brain)

El backend debe ser capaz de manejar ambas monedas simultáneamente, independientemente de cuál sea la "Principal" en ese momento.

### A. Automatización BCV Dual (Full-Duplex)

El servicio cron (`ir.cron`) conectado a la librería `pyDolarVenezuela` ejecutará la siguiente lógica cada mañana (8:00 AM):

1. **Fetch Universal:** Descarga **simultáneamente** la tasa del DÓLAR y del EURO del BCV.
2. **Persistencia:** Guarda ambas tasas en el modelo `res.currency`.
3. **Lógica de "La Moneda Reina":**
   - Verifica cuál es la `Moneda Operativa Principal` configurada hoy.
   - Si es **EURO**: Valida la integridad de la tasa EUR con mayor rigor.
   - Si es **DÓLAR**: Valida la integridad de la tasa USD con mayor rigor.

### B. Control Híbrido (Auto/Manual) por Moneda

En el modelo de Monedas (`res.currency`), mantendremos controles independientes:

- `USD`: [Switch Auto/Manual] | [Valor Manual]
- `EUR`: [Switch Auto/Manual] | [Valor Manual]

*Esto garantiza que si decides cambiar tu operación de Euro a Dólar mañana, la tasa del Dólar ya estará actualizada y lista para usarse.*

### C. Gestión de IGTF (Impuesto a Grandes Transacciones)

Panel de configuración con lógica condicional:

- **Interruptor Global:** `[ x ] Habilitar Cobro de IGTF (3%)`.
- Si está **OFF**: El sistema elimina cualquier lógica de impuesto adicional.
- Si está **ON**: Se activa el selector de comportamiento:
  - *Opción:* "Aplicar a todas las divisas extranjeras".

- **Botón de Excepción Rápida:** Un botón de pánico en ajustes para "Suspender IGTF temporalmente" sin desinstalar el módulo.

## 3. Frontend: Experiencia POS de Clase Mundial (UX/UI)

Diseño de interfaz basado en el framework **Odoo OWL (Odoo Web Library)**, optimizado para pantallas táctiles.

### A. El Widget Inteligente (Navbar Superior)

El elemento visual en la caja se adapta a la decisión gerencial tomada en el Backend.

- **Ubicación:** Barra superior derecha.
- **Comportamiento Dinámico:**
  - **Escenario 1 (Principal = EURO):**
    - Muestra grande: `🇧🇪 1€ = 68.50 Bs`.
    - Muestra pequeño (subtítulo): `🇺🇸 1$ = 62.10 Bs`.
  - **Escenario 2 (Principal = DÓLAR):** (Al cambiar la configuración)
    - Muestra grande: `🇺🇸 1$ = 62.10 Bs`.
    - Muestra pequeño (subtítulo): `🇧🇪 1€ = 68.50 Bs`.

- **Indicadores de Estado:**
  - 🟢 (Auto) / 🟠 (Manual) / 🔴 (Error/Desactualizado).

### B. Modal de Control "Touch-First" (Interacción)

Al tocar el Widget, se abre el panel de control.

- **Diseño:** Ventana modal flotante con botones grandes.
- **Funcionalidad:**
  1. **Toggle de Modo:** Un switch grande para la moneda principal. "Pasar a Manual".
  2. **Input Numérico:** Teclado numérico en pantalla para ajustar la tasa rápidamente.
  3. **Botón Sincronizar:** "Forzar lectura BCV ahora".
  4. **Botón de Emergencia:** "Cambiar Moneda Principal en este POS". (Opcional, protegido por contraseña de Gerente). *Esto permite que, si se acaban los Euros en caja, el gerente pueda virar la operación a Dólares en segundos.*

## 4. Flujo de Venta y Automatización (El "Viaje del Dato")

1. **Configuración Inicial:** Gerencia decide: "Esta semana operamos en **Dólares**". Selecciona USD en ajustes.
2. **Apertura de Caja:** El POS carga. Todos los productos (Hamburguesas, Bebidas) se muestran automáticamente en **USD**.
3. **Cobro:**
   - Total a pagar: **10 USD**.
   - Cliente dice: "Pago en Bolívares".
   - Sistema calcula: `10 * Tasa_BCV_USD`. Muestra: `621.00 Bs`.
4. **Pago Mixto (El Reto Real):**
   - Cliente: "Tengo 5 Euros y el resto en Pago Móvil".
   - Sistema:
     - Recibe 5 EUR -> Lo convierte a USD (usando la tasa cruzada interna EUR/USD) para restar de la deuda.
     - Resta el saldo en Bs.
5. **Facturación Fiscal:**
   - La impresora fiscal recibe el monto total convertido a **Bolívares** (La única verdad para el SENIAT).

## 5. Ingeniería de Robustez (Safety Measures)

Requerimientos no funcionales para el programador:

1. **Protección de Arbitraje:** El sistema debe impedir que la "Tasa Manual" tenga una discrepancia mayor al 5% con la tasa oficial sin una autorización de doble factor (Contraseña de Supervisor).
2. **Caché de Supervivencia:** Si el servicio BCV falla por 3 días seguidos, el sistema debe alertar: "Usando tasa de hace 72h. Por favor actualizar manual", pero **NUNCA** debe detener la venta ni poner la tasa en 0.
3. **Logs de Auditoría IGTF:** Cada vez que se desactiva el cobro de IGTF, debe quedar registrado quién lo hizo y a qué hora.

## 6. Checklist de Entregables (Para el Desarrollador)

- **[Backend] Modelo `res.config.settings`:** Agregar campo `operational_currency_id` y lógica de cambio de tarifa.
- **[Backend] Integración BCV:** Script robusto que traiga SIEMPRE USD y EUR, y los almacene.
- **[POS] Componente OWL:** Widget reactivo que cambie el orden de las monedas (USD/EUR) según la configuración.
- **[POS] Lógica de Precios:** Override del `ProductScreen` para mostrar precios en la moneda operativa elegida.
- **[Fiscal] IGTF:** Botón ON/OFF en ajustes que inyecte o remueva la línea de impuesto en el `OrderLine`.

**Conclusión del Ingeniero:**  
Este diseño permite una **flexibilidad total**. Tu negocio no queda "casado" con el Euro. Si la economía cambia, tu sistema cambia con un solo clic, manteniendo la legalidad ante el SENIAT intacta y ofreciendo a tus cajeros una herramienta que elimina el estrés de calcular cambios mentalmente.
