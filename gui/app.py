import streamlit as st
import shacl_maker as sm


def main():
    st.set_page_config(layout="wide")

    if 'odtp-input' not in st.session_state:
        st.session_state['odtp-input'] = 'Please run the analysis'

    if 'odtp-output' not in st.session_state:
        st.session_state['odtp-output'] = 'Please run the analysis'

    if 'input' not in st.session_state:
        st.session_state['input'] = 'Load a file or write a new one'

    col1, col2 = st.columns(2)

    # Set up the sidebar
    st.sidebar.title("ODTP SHACL MAKER")
    st.sidebar.write("Description")

    with col1:
        # Set up the main content
        st.title("Input Data")
        button0 = st.button("Make SHACL")
        input_text = st.text_input("URL Input (not available)")
        uploaded_file = st.file_uploader("Upload File")

        if uploaded_file:
            file_string = uploaded_file.read()
            with open("/data/odtp.yml", "wb") as file:
                file.write(file_string)

            st.session_state['input'] = file_string.decode("utf-8")

            st.write(uploaded_file.name)

        long_text = st.code(st.session_state['input'], language="yaml")
            
        

        if button0:
            output = sm.main("/data")
            #output = sm.main(uploaded_file.name)
            with open("/data/input.ttl", "r") as file:
                input_shapes = file.read()

            st.session_state['odtp-input'] = input_shapes

            with open("/data/output.ttl", "r") as file:
                output_shapes = file.read()

            st.session_state['odtp-output'] = output_shapes

    with col2:
        st.title("Output Area")
        col3, col4 = st.columns(2)

        with col3:
            if button0:
                with open("/data/input.ttl", "rb") as file:
                    button1 = st.download_button(
                    label="Download odtp-input.ttl",
                    data=file,
                    file_name="odtp-input.ttl",
                    mime="text/ttl",
                    )

        with col4:
            if button0:
                with open("/data/output.ttl", "rb") as file:
                    button2 = st.download_button(
                    label="Download odtp-output.ttl",
                    data=file,
                    file_name="odtp-output.ttl",
                    mime="text/ttl",
                    )

        tab1, tab2 = st.tabs(["odtp-input.ttl", "odtp-output.ttl"])

        with tab1:
            odtp_input = st.code(st.session_state['odtp-input'], language='turtle')
        
        with tab2:
            odtp_output = st.code(st.session_state['odtp-output'], language='turtle')

if __name__ == "__main__":
    main()