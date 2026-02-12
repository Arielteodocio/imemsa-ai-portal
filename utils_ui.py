import streamlit as st

def apply_global_style():
    """CSS global para todas las páginas."""
    st.markdown(
        """
<style>
/* Título tipo "Tipos de Cambio" */
.imemsa-title{
  font-size: 64px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0;
  color: #1f2937;
}

/* Subtítulo opcional */
.imemsa-subtitle{
  margin-top: 10px;
  font-size: 18px;
  color: rgba(31,41,55,0.75);
}

/* Línea bicolor */
.imemsa-divider{
  height: 10px;
  width: 100%;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    #0b4ea2 0%,
    #0b4ea2 45%,
    #e11d2e 45%,
    #e11d2e 55%,
    #0b4ea2 55%,
    #0b4ea2 100%
  );
  margin: 22px 0 26px 0;
}
</style>
""",
        unsafe_allow_html=True,
    )

def render_title(title: str, subtitle: str | None = None):
    """Renderiza título + línea bicolor."""
    apply_global_style()
    st.markdown(f'<h1 class="imemsa-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="imemsa-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<div class="imemsa-divider"></div>', unsafe_allow_html=True)
