from shiny import App, reactive, render, ui, module

@module.ui
def download_csv_cxt_attr_ui():
    return ui.layout_columns(
                ui.h1(),
                ui.download_button("download_df", "Download Context CSV", class_="btn btn-outline-primary",style="text-align: center; font-size: 12px; width: 190px;"),
                ui.download_button("download_cxt", "Download Context CXT", class_="btn btn-outline-primary",style="text-align: center; font-size: 12px; width: 190px;"),
                ui.h1(),
                col_widths=(2,4, 4,2)
                ),

@module.server
def row_server(input, output, session,obj):
    state = reactive.value(None)

    @reactive.effect
    @reactive.event(input.text_in)
    def set_state():
        obj.set("now i have set this state from module")
        state.set(input.text_in())


    @output
    @render.text
    def text_out():
        states = state.get()
        obj.get()
        return f'You entered "{states}" {obj.get()}'