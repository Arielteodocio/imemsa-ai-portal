import streamlit as st

def apply_imemsa_style():
    """CSS global: tipografía de título + línea bicolor."""
    st.markdown(
        """
<style>
.imemsa-title{
  font-size: 64px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.05;
  margin: 0;
  color: #1f2937;
}
.imemsa-subtitle{
  margin-top: 10px;
  font-size: 18px;
  color: rgba(31,41,55,0.75);
}
.imemsa-divider{
  height: 10px;
  width: 100%;
  border-radius: 999px;
  background: linear-gradient(
    90deg,
    #0A4FA3 0%,
    #0A4FA3 45%,
    #E32028 45%,
    #E32028 55%,
    #0A4FA3 55%,
    #0A4FA3 100%
  );
  margin: 22px 0 26px 0;
}
</style>
""",
        unsafe_allow_html=True,
    )

def render_title(title: str, subtitle: str | None = None):
    """Renderiza título estándar + línea bicolor."""
    apply_imemsa_style()
    st.markdown(f'<h1 class="imemsa-title">{title}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="imemsa-subtitle">{subtitle}</div>', unsafe_allow_html=True)
    st.markdown('<div class="imemsa-divider"></div>', unsafe_allow_html=True)
