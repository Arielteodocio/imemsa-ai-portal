def tools_landing_screen():
    # Sidebar con controles extra
    tools_sidebar_controls()

    top_brand()

    st.markdown("## 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar. También puedes navegar desde el menú lateral.")

    st.write("")

    # ---- Ajusta estos paths exactamente a tus archivos dentro de /pages ----
    modules = [
        {
            "title": "Transcripción",
            "emoji": "🎧",
            "desc": "Convierte audio en español a texto listo para copiar o exportar.",
            "page": "1_🎧_Transcripcion.py",
        },
        {
            "title": "Traducción",
            "emoji": "🌐",
            "desc": "Traduce texto Inglés ↔ Español con formato claro y profesional.",
            "page": "2_🌐_Traduccion.py",
        },
        {
            "title": "Minutas y acciones",
            "emoji": "📝",
            "desc": "Genera minuta estructurada y lista de acciones con responsables y fechas.",
            "page": "3_📝_Minutas_y_acciones.py",
        },
        {
            "title": "Documentos",
            "emoji": "📄",
            "desc": "Extrae información de PDFs/escaneos (OCR) y crea exportables.",
            "page": "4_📄_Documentos.py",
        },
        {
            "title": "Forecast y anomalías",
            "emoji": "📈",
            "desc": "Pronóstico + detección de desviaciones para análisis rápido.",
            "page": "5_📈_Forecast_y_Anomalias.py",
        },
        {
            "title": "NLP Operación",
            "emoji": "🧠",
            "desc": "Clasifica solicitudes internas, prioridad, área destino y datos clave.",
            "page": "6_🧠_NLP_Operacion.py",
        },
    ]

    # ---- Estilo cards (sutil y corporativo) ----
    st.markdown(
        """
        <style>
        .card {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 18px 18px 14px 18px;
            background: rgba(255,255,255,0.03);
            min-height: 170px;
        }
        .card h3 {
            margin: 0 0 6px 0;
            font-size: 1.25rem;
        }
        .card p {
            margin: 0;
            opacity: 0.85;
            line-height: 1.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Grid 3 columnas ----
    cols = st.columns(3, gap="large")

    for i, m in enumerate(modules):
        with cols[i % 3]:
            with st.container():
                st.markdown(
                    f"""
                    <div class="card">
                      <h3>{m["emoji"]} {m["title"]}</h3>
                      <p>{m["desc"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Abrir", key=f"open_{i}", use_container_width=True, type="primary"):
                        st.switch_page(m["page"])
                with c2:
                    st.button("Info", key=f"info_{i}", use_container_width=True)

                # Acción para "Info"
                if st.session_state.get(f"info_{i}", False):
                    st.toast(f'{m["title"]}: {m["desc"]}', icon="ℹ️")

