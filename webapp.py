import streamlit as st


top_image = 'images/ARKANA_LOGO.png'
st.image(top_image, width=75)

# @st.cache_resource()


# q1_sales = {
#     'January': 100,
#     'February': 110,
#     'March': 115
# }
#
# q2_sales = {
#     'April': 150,
#     'May': 200,
#     'June': 250
# }
# q2_df = pd.DataFrame(q2_sales.items(),
#                      columns=['Month', 'Amount'])
# #
# q1_df = pd.DataFrame(q1_sales.items(),
#                      columns=['Month', 'Amount'])
#

def get_redcap_urls():
    # st.write("Redcap UAT [link](https://uat.redcapcloud.com/#cid=nph2000&act=list)")
    st.write("")
    st.write('')
    st.write(f'''
        <a target="_self" href="https://www.build.redcapcloud.com/#cid=nph2000&act=list">
            <button>
                RedCap BUILD
            </button>
        </a>
        ''',
             unsafe_allow_html=True
             )
    st.write("")
    st.write('')
    st.write(f'''
            <a target="_self" href="https://uat.redcapcloud.com/#cid=nph2000&act=list">
                <button>
                    RedCap UAT
                </button>
            </a>
            ''',
             unsafe_allow_html=True
             )
    st.write("")
    st.write('')
    st.write(f'''
            <a target="_self" href="https://login.redcapcloud.com/">
                <button>
                    RedCap PROD
                </button>
            </a>
            ''',
             unsafe_allow_html=True
             )


