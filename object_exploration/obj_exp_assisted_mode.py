from shiny import App, reactive, render, ui, module

@module.ui
def obj_exp_assisted_mode_ui():
    return ui.card(
                ui.div(
                    ui.output_ui("render_starting_ui_assisted_mode_object"),
                    ui.output_ui("render_current_obj_implication_output_assisted_mode"),
                ),
                ui.div(
                ui.output_ui("model_response_output_assisted_mode_object"),
                ),
                ui.div(
                    ui.output_ui("model_response_button_assisted_mode_object"),
                    ui.output_ui("model_response_action_button_assisted_mode_object"),
                    ui.output_ui("render_manual_input_controls_object"),
                    ui.output_ui("render_implication_message_ui_object"),
                ),
            )

@module.server
def obj_exp_assisted_mode_server(input, output, session, cxt, trigger_recalc, selected_obj_index):
    toggle_state_assisted_mode_object = reactive.Value(True)
    implication_message_assisted_state_object = reactive.value(None)
    manual_input_toggle_assisted_mode_object = reactive.value(False)
    models_response_state_object = reactive.value(None)
    prompt_body_state_object = reactive.value([{"role": "system", "content": "Return all outputs in json format"}])

    @output
    @render.ui
    def render_starting_ui_assisted_mode_object():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.", style="color: red; margin-top: 100px; margin-left: 30px;"),
                style="margin-top: 30px; margin-left: 24px;"
            )
        else:
            return ui.div("")

    @output
    @render.ui
    def render_current_obj_implication_output_assisted_mode():
        _ = trigger_recalc.get()
        context = cxt.get()
        if context is not None:
            implication = context.Basic_Exploration.get_current_object_implications(selected_obj_index.get())
            return ui.div(
                ui.strong(f"Current Implication : {implication}"),
                style="text-align: center; margin-top: 45px; margin-bottom: 30px;",
            )
        return ui.div("")

    @output
    @render.ui
    def model_response_button_assisted_mode_object():
        context = cxt.get()
        if context is not None:
            return ui.div(
                ui.div(
                    ui.input_action_button("get_model_response_object", "Ask the Model",
                                           class_="btn btn-outline-primary",
                                           style="margin-top: 20px;", ),
                    ui.p("^ Please wait while the response is being generated. Press the button only once.",
                         style="font-size: 12px; margin-top: 10px; margin-bottom: 0px;"),
                    ui.p("# If the response is unsatisfactory, you may press the button again to regenerate it.",
                         style="font-size: 12px; margin-top: 0px; margin-bottom: 0px;"),

                    style="display: flex; flex-direction: column; align-items: center;"
                )
            )
        else:
            return ui.div()

    @output
    @render.ui
    def model_response_action_button_assisted_mode_object():
        context = cxt.get()
        if context is not None and models_response_state_object.get() is not None:
            return ui.div(
                ui.layout_columns(
                    ui.h3(""),
                    ui.div(
                        ui.input_action_button("confirm_model_response_object", "Confirm Model Response",
                                               class_="btn-success",
                                               style="margin-top: 20px;", ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.input_action_button("reject_model_response_object", "Manual Input", class_="btn-warning",
                                               style="margin-top: 20px;", ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.h3(""),
                    col_widths=(1, 5, 5, 1),
                )
            )
        else:
            return ui.div("")

    @output
    @render.ui
    def model_response_output_assisted_mode_object():
        model_response = models_response_state_object.get()
        if model_response is not None:
            result = model_response
            if result['output'] == "YES":
                return ui.card(
                    ui.h5(f"Agents's Response:"),
                    ui.div(f"The agent say's the implication is valid"),
                )
            else:
                return ui.div(
                    ui.h6("Agent's Response:", style="font-weight: bold; margin-bottom: 4px;"),
                    ui.HTML(
                        "<div style='margin-bottom: 0px;'>The agent indicates that the implication is invalid.</div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px;'>Suggested counterexample meaning: <strong>{result['meaning']}</strong></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0;'>Verb(s) associated with this meaning: <strong>{', '.join(result['verbs'])}</strong></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px; margin-top:20px'><em>Explanation given by the Agent: {result['explanation']}</em></div>"),
                    ui.HTML(
                        f"<div style='margin-bottom: 0px; margin-top:20px'><em>Example given by the Agent: {result['example']}</em></div>"),
                    style="text-align: center;"
                )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.get_model_response_object)
    def handle_model_response_generation_object():
        context = cxt.get()
        implication_message_assisted_state_object.set("")
        manual_input_toggle_assisted_mode_object.set(False)
        if context is not None:

            attributes = context.Basic_Exploration.attributes
            objects = context.Basic_Exploration.objects

            premise, conclusion = context.Basic_Exploration.get_object_implication_premise_conclusion_for_prompt(
                selected_obj_index.get())
            
            prompt = set_prompt_object(
                objects=objects,
                frames=attributes,
                premise_verbs=premise,
                conclusion_verbs=conclusion)

            set_prompts = prompt_body_state_object.get()
            set_prompts.append({"role": "user", "content": prompt})

            result_str, result = evaluate_prompt_chat(set_prompts)

            set_prompts.append({"role": "assistant", "content": result_str})
            prompt_body_state_object.set(set_prompts)

            current_implication = context.Basic_Exploration.get_current_object_implications(selected_obj_index.get())

            implication_message_assisted_state_object.set(
                ui.accordion(
                    ui.accordion_panel("Chat with the agent",
                                       ui.card(
                                           ui.card_header("FCA ChatBot"),
                                           ui.chat_ui("chat_obj", messages=["You can chat with the agent here"],
                                                      width="100%"),
                                           style="width:min(680px, 100%)",
                                           class_="mx-auto",
                                       ),
                                       ),
                    ui.accordion_panel("Prompt sent to the agent",
                                       ui.HTML(f"<pre>"
                                               f"Implication being tested:\n"
                                               f"{current_implication}\n\n\n"
                                               f"Prompt sent to the agent for this implication:\n\n"
                                               f"{prompt}"
                                               f"</pre>"),
                                       ),
                    id="acc",
                    open=False,
                ),
            )

            result = evaluate_prompt(prompt)
            models_response_state_object.set(result)
        else:
            models_response_state_object.set(None)

    chat_obj = ui.Chat(id="chat_obj")

    @chat_obj.on_user_submit
    async def handle_user_chat_input_object(user_input: str):
        input_chat = user_input.strip()
        context = cxt.get()
        if context is not None:

            set_prompts = prompt_body_state_object.get()
            add_on_prompt = ""
            if "format" in input_chat:
                add_on_prompt = " and don't respond with a json object from now on, until asked"
            set_prompts.append({"role": "user", "content": f"{input_chat},{add_on_prompt}"})
            result_str = evaluate_prompt_chat_test(set_prompts)
            set_prompts.append({"role": "assistant", "content": result_str})
            prompt_body_state_object.set(set_prompts)

            if "output" in result_str:
                try:
                    response_json = json.loads(result_str)
                    models_response_state_object.set(response_json)
                    print("this may be a solution")
                except Exception as e:
                    print(e)

            message = result_str
            await chat_obj.append_message(message)

    @reactive.effect
    @reactive.event(input.reject_model_response_object)
    def handle_manual_input_controls_object():
        manual_input_toggle_assisted_mode_object.set(True)
        implication_message_assisted_state_object.set("")

    @reactive.effect
    @reactive.event(input.confirm_model_response_object)
    def handle_confirm_model_response_object():
        manual_input_toggle_assisted_mode_object.set(False)
        toggle_state_assisted_mode_object.set(True)

        model_response = models_response_state_object.get()

        if model_response is not None:
            if model_response['output'] == "NO":
                context = cxt.get()
                counter_example_meaning = model_response["meaning"]
                counter_example_verbs = model_response["verbs"]

                out = context.Basic_Exploration.set_counter_example_object(counter_example_meaning, counter_example_verbs,
                                                                       selected_obj_index.get())

                if out[0] == "PASS":
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    a = "Previous Model Response Confirmed, Counter Examples added."
                    b = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                    implication_message_assisted_state_object.set(b)

                if out[0] == "FAIL":
                    a = "Previous Model Response is invalid, Please generate model response again."
                    b = ui.div(
                        ui.h6(f'{a}', style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                    )
                    implication_message_assisted_state_object.set(b)

                implication_message_assisted_state_object.set(b)
                models_response_state_object.set(None)
            else:
                trigger_recalc.set(trigger_recalc.get() + 1)
                context = cxt.get()
                context.Basic_Exploration.post_confirm_object_implications(selected_obj_index.get())
                a = "Previous Model Response Confirmed, Implication confirmed."
                b = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                implication_message_assisted_state_object.set(b)
                models_response_state_object.set(None)
        else:
            implication_message_assisted_state_object.set("")

    @output
    @render.ui
    def render_manual_input_controls_object():
        if manual_input_toggle_assisted_mode_object():
            if toggle_state_assisted_mode_object():
                reject = ui.input_action_button(
                    "toggle_button_assisted_mode_object", "reject implication",
                    class_="btn btn-outline-warning", style="margin-top: 20px; width: 250px;",
                )
            else:
                reject = ui.input_action_button(
                    "toggle_button_assisted_mode_object", "confirm counter example",
                    class_="btn btn-outline-primary", style="margin-top: 20px; width: 250px;")

            a = ui.div(
                ui.h6("Provide Manual Input:", style="text-align:center;font-weight: bold; margin-bottom: 4px;"),
                ui.layout_columns(
                    ui.h3(""),
                    ui.input_action_button("confirm_implication_assisted_mode_object", "confirm implication",
                                           class_="btn btn-outline-success",
                                           style="margin-top: 20px;width: 250px;", ),
                    reject,
                    ui.h3(""),
                    col_widths=(1, 5, 5, 1),
                ))
            return a
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.toggle_button_assisted_mode_object)
    def handle_toggle_button_click_object():
        if toggle_state_assisted_mode_object():
            trigger_recalc.set(trigger_recalc.get() + 1)
            _, objects, _, _ = context_data()
            obj = objects
            out = ui.div(
                ui.h6(f'Implication Rejected',
                      style="color: Red; text-align: center; font-weight: bold; margin-top: 20px;"),
                ui.h6(f'Provide Counter Example below',
                      style="color: Black; text-align: center; margin-top: 20px; margin-bottom: 20px;"),
                ui.layout_columns(
                    ui.div(
                        ui.h6("Enter Counter Object", style="margin-bottom: 20px;"),
                        ui.input_text("counter_object_text_assisted_mode_object", "", "object"),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                    ui.div(
                        ui.h6("Enter Counter Object's Attributes", style="margin-bottom: 20px;"),
                        ui.input_checkbox_group(  # <<
                            "counter_attribute_checkbox_assisted_mode_object",  # <<
                            "",
                            obj,
                        ),
                        style="display: flex; flex-direction: column; align-items: center;"
                    ),
                ),
            )
            implication_message_assisted_state_object.set(out)

        else:
            try:
                context = cxt.get()
                counter_object = input.counter_object_text_assisted_mode_object()
                counter_attributes = input.counter_attribute_checkbox_assisted_mode_object()
                out = context.Basic_Exploration.set_counter_example_object(counter_object, counter_attributes,
                                                                       selected_obj_index.get())
                if out[0] == "PASS":
                    trigger_recalc.set(trigger_recalc.get() + 1)
                    a = "Previous Counter Example has been Confirmed."
                    b = ui.h6(f'{a}', style="color: Blue; text-align: center; font-weight: bold;")
                    implication_message_assisted_state_object.set(b)

                if out[0] == "FAIL":
                    a = "Counter Example is invalid."
                    b = ui.div(
                        ui.h6(f'{a}', style="color: Red; text-align: center; font-weight: bold;"),
                        ui.h6(f'{out[1]}', style="color: Red; text-align: center; font-weight: bold;")
                    )
                    implication_message_assisted_state_object.set(b)
            except Exception as e:
                pass
        toggle_state_assisted_mode_object.set(not toggle_state_assisted_mode_object())

    @reactive.effect
    @reactive.event(input.confirm_implication_assisted_mode_object)
    def handle_manual_implication_confirmation_object():
        if input.confirm_implication_assisted_mode_object():
            trigger_recalc.set(trigger_recalc.get() + 1)
            context = cxt.get()
            if context is not None:
                toggle_state_assisted_mode_object.set(True)
                context.Basic_Exploration.post_confirm_object_implications(selected_obj_index.get())
                a = "Previous Implication Confirmed."
                b = ui.h6(f'{a}', style="color: Green; text-align: center; font-weight: bold;")
                implication_message_assisted_state_object.set(b)
        else:
            implication_message_assisted_state_object.set("")

    @output
    @render.ui
    def render_implication_message_ui_object():
        a = implication_message_assisted_state_object.get()
        if a is not None:
            a = implication_message_assisted_state_object.get()
            return ui.div(a)
        else:
            return ui.div("")