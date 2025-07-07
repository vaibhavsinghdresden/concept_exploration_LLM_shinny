from shiny import App, reactive, render, ui, module

@module.ui
def obj_exp_auto_mode_ui():
    return ui.card(
                 ui.div(
                     ui.output_ui("starting_mode_ui_auto_mode_object"),
                 ),
                ui.div(
                    ui.output_ui("show_select_number_of_steps_obj"),
                    ui.output_ui("show_start_exploration_button_auto_mode_object"),
                    ui.output_ui("show_exploration_log_text_auto_mode_object"),
                 ),
            )

@module.server
def obj_exp_auto_mode_server(input, output, session, cxt, trigger_recalc):
    models_response_log_auto_object = reactive.value(None)
    trigger_response_object = reactive.value(None)
    prompt_body_state_auto_obj = reactive.value([{"role": "System",
                                                  "content": "Please give the counter example words in English, Dutch, Russian, French and Dutch"}])
    steps_state_obj = reactive.value(10)

    @output
    @render.ui
    def starting_mode_ui_auto_mode_object():
        context = cxt.get()
        if context is None:
            return ui.div(
                ui.strong(f"Action requires an input file.",
                          style="color: red; margin-top: 100px; margin-left: 30px;"),
                style="margin-top: 30px; margin-left: 24px;"
            )
        else:
            return ui.div("")

    @output
    @render.ui
    def show_select_number_of_steps_obj():
        context = cxt.get()
        if context is not None:
            return ui.layout_columns(
                ui.input_text_area("system_prompt_obj", "System Prompt",
                                   "You're a logical and deep reasoner, please give the counter example words in English, Dutch, Russian, French and Dutch"),
                ui.input_numeric("steps_obj", "Objects to confirm before stopping", 10, min=1, max=3000),
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.system_prompt_obj)
    def set_number_of_steps_obj():
        if input.system_prompt_obj() is not None:
            prompt = [{"role": "System", "content": input.system_prompt_obj()}]
            prompt_body_state_auto_obj.set(prompt)

    @reactive.effect
    @reactive.event(input.steps_obj)
    def set_number_of_steps_obj():
        if steps_state_obj.get() is not None:
            steps_state_obj.set(input.steps_obj())

    @output
    @render.ui
    def show_start_exploration_button_auto_mode_object():
        context = cxt.get()
        if context is not None:
            return ui.div(
                ui.input_action_button("start_exploration_object", "Start Exploration", class_="btn-success",
                                       style="margin-top: 10px;width: 250px;", ),
                ui.strong("❗️❗❗️This process starts from the first implication by default",
                          style="font-size: 12px;color:red; margin-top: 10px;"),
                ui.p("^ Please press the button only once",
                     style="font-size: 12px; margin-top: 10px; margin-bottom: 0px;"),
                ui.p("^ The process will only end once the exploration is complete", style="font-size: 12px;"),
                style="display: flex; flex-direction: column; align-items: center;"
            )
        else:
            return ui.div("")

    @reactive.effect
    @reactive.event(input.start_exploration_object)
    def set_start_exploration_text_object():
        if input.start_exploration_object():
            trigger_response_object.set("Start")

    @reactive.effect
    def run_exploration_object():
        if trigger_response_object.get() == "Start":
            context = cxt.get()
            if context is not None:
                imp_index_auto_obj = 0
                i = 0
                while context.Basic_Exploration.get_current_object_implications() is not None and i < int(
                        steps_state_obj.get()) and imp_index_auto_obj < len(
                        context.Basic_Exploration.get_object_implications()):
                    i += 1
                    last_implication = context.Basic_Exploration.get_current_object_implications()
                    premise, conclusion = context.Basic_Exploration.get_object_implication_premise_conclusion_for_prompt()
                    attr = context.Basic_Exploration.get_current_attributes()
                    objects = context.Basic_Exploration.get_current_objects()

                    prompt = set_prompt_object(
                        objects=objects,
                        frames=attr,
                        premise_verbs=premise,
                        conclusion_verbs=conclusion
                    )

                    set_prompts = prompt_body_state_auto_obj.get()
                    set_prompts.append({"role": "user", "content": prompt})

                    result_str, result = evaluate_prompt_chat(set_prompts)
                    set_prompts.append({"role": "assistant", "content": result_str})

                    print("-------------------------------------")
                    print("Prompt Size : ", len(set_prompts))
                    print(i, " : ", last_implication)
                    print("no of attributes : ", len(attr))
                    print("No of implications left (currently before adding counter example): ",
                          len(context.Basic_Exploration.get_object_implications()) - 1)

                    if len(set_prompts) > 20:
                        print("rejected thrice, accepting the implication now")
                        context.Basic_Exploration.post_confirm_object_implications_implications(imp_index_auto_obj)
                        imp_index_auto_obj += 1
                        prompt_body_state_auto_obj.set([{"role": "System", "content": input.system_prompt_obj()}])
                        continue

                    if result["output"] == "NO" and result["meaning"] in attr:
                        print(f"Object: {result["meaning"]} already present in the context")
                        context.Basic_Exploration.delete_attribute(result["meaning"])
                        set_prompts.append(
                            {"role": "user",
                             "content": f"meaning already present in the context, please use another counterexample, or confirm the hypothesis."})
                        result_str, result = evaluate_prompt_chat(set_prompts)
                        set_prompts.append({"role": "assistant", "content": result_str})
                        prompt_body_state_auto_obj.set(set_prompts)
                        continue

                    if result["output"] == "NO":
                        context = cxt.get()
                        try:
                            out = context.Basic_Exploration.set_counter_example_object(result["meaning"], result["verbs"],
                                                                                   imp_index_auto_obj)
                            if out[0] == "PASS":
                                print("The model gave counter example : ", result["meaning"],
                                      "With associated Verbs : ", result["verbs"])
                                trigger_recalc.set(trigger_recalc.get() + 1)
                                models_response_log_auto_object.set(
                                    ui.div(models_response_log_auto_object.get(),
                                           ui.card(
                                               ui.div(
                                                   ui.strong(
                                                       f'For implication : {last_implication}'),
                                                   ui.HTML(
                                                       f"<div>Model suggested that the implication is invalid and</div>"),
                                                   ui.HTML(
                                                       f"<div>Suggested meaning: <strong>{result['meaning']}</strong></div>"),
                                                   ui.HTML(
                                                       f"<div>With meanings: <strong>{', '.join(result['verbs'])}</strong></div>"),
                                                   ui.HTML(
                                                       f"<div style='margin-bottom: 0px; margin-top:20px'>Explanation given by the Agent: <em>{result['explanation']}</em></div>"),

                                               )
                                           )
                                           )
                                )
                                prompt_body_state_auto_obj.set([{"role": "System", "content": input.system_prompt()}])

                            elif out[0] == "FAIL":
                                print("exception has been occurred", out[1])
                                set_prompts.append(
                                    {"role": "user",
                                     "content": f"the current example that you provided is invalid as {out[1]}"})
                                result_str, result = evaluate_prompt_chat(set_prompts)
                                set_prompts.append({"role": "assistant", "content": result_str})
                                prompt_body_state_auto_obj.set(set_prompts)

                        except Exception as e:
                            _ = _

                    else:
                        trigger_recalc.set(trigger_recalc.get() + 1)
                        context.Basic_Exploration.post_confirm_object_implications(imp_index_auto_obj)
                        models_response_log_auto_object.set(ui.div(
                            models_response_log_auto_object.get(),
                            ui.strong(f'For implication : {last_implication}'),
                            ui.h6("Model confirmed the implication.", style="color:blue; font-weight:bold;")
                        )
                        )
                        prompt_body_state_auto_obj.set([{"role": "System", "content": input.system_prompt()}])

                print("--EXPLORATION ENDS--")

    @output
    @render.ui
    def show_exploration_log_text_auto_mode_object():
        model_log = models_response_log_auto_object.get()
        if model_log is not None:
            return ui.div(
                ui.h6("Exploration completed. The model carried out the following operations:",
                      style="text-align: center; color:green; font-weight:bold; margin-top: 20px;"),
                model_log
            )
        else:
            return ui.div("")