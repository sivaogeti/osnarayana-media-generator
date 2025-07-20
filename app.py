# Reordered UI
st.caption("Built by O.S.Narayana ❤️ using Streamlit + ElevenLabs + Unsplash")
st.title("🎮 Welcome to OSN Media Generator")

# Collapsed Settings with Reset
with st.expander("⚙️ Settings", expanded=False):
    ...
    if st.button("♻️ Reset"):
        st.session_state.clear()
        st.experimental_rerun()

# Detect Dark Mode from device/browser (if JS injected or default set)
dark_mode = st.get_option("theme.base") == "dark"
...

# Vertical Tabs Styling (experimental improvement for mobile users)
st.markdown("""
<style>
.css-1d391kg { flex-direction: column !important; }
</style>
""", unsafe_allow_html=True)
