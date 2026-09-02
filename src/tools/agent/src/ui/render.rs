use ratatui::{
    layout::{Constraint, Direction, Layout},
    style::{Color, Style},
    widgets::{Block, Borders, List, ListItem, Paragraph},
    Frame,
};
use crate::ui::app::{App, AgentStatus};

pub fn draw_dashboard(f: &mut Frame, app: &App) {
    let telemetry_height = if app.scroll > 0 { 3 } else { 6 };
    let mobile_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(telemetry_height), // Top: Swarm Telemetry
            Constraint::Min(5),    // Middle: Chat History
            Constraint::Length(3), // Bottom: Command Deck
        ])
        .split(f.size());

    let spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];
    let frame = spinner[app.tick % spinner.len()];

    let (status_text, status_color) = match &app.status {
        AgentStatus::Idle => ("🟢 Status: Idle".to_string(), Color::Cyan),
        AgentStatus::Thinking(agent) => (format!("{} Thinking: {}", frame, agent), Color::Magenta),
        AgentStatus::ExecutingTool(tool) => (format!("{} Executing: {}", frame, tool), Color::Yellow),
        AgentStatus::Distilling => (format!("{} Distilling Prompt...", frame), Color::Blue),
        AgentStatus::Downloading(prog) => (format!("{} Downloading: {:.1}%", frame, prog * 100.0), Color::Blue),
    };
    
    let theme_rgb = Color::Rgb(app.config.theme_primary[0], app.config.theme_primary[1], app.config.theme_primary[2]);
    let text_rgb = Color::Rgb(app.config.theme_text[0], app.config.theme_text[1], app.config.theme_text[2]);
    
    let mut header_items = vec![ListItem::new(status_text).style(Style::default().fg(status_color))];
    
    // Only show active swarm details if we aren't scrolling up
    if app.scroll == 0 {
        if !app.active_sub_agents.is_empty() {
            let subs = app.active_sub_agents.join(" | ");
            header_items.push(ListItem::new(format!("↳ Active Swarm: [{}]", subs)).style(Style::default().fg(Color::Yellow)));
        } else {
            header_items.push(ListItem::new("↳ Active Swarm: [None]").style(Style::default().fg(Color::DarkGray)));
        }
    }

    let telemetry_list = List::new(header_items).block(
        Block::default().borders(Borders::ALL).title(if app.scroll > 0 { " Telemetry (Minimal) " } else { " Swarm Telemetry " }).style(Style::default().fg(theme_rgb))
    );
    f.render_widget(telemetry_list, mobile_chunks[0]);

    // --- Render Chat Window (Middle) ---
    let chat_title = if app.scroll > 0 {
        format!(" Master ReAct Loop (Scrolled {}) ", app.scroll)
    } else {
        " Master ReAct Loop ".to_string()
    };
    
    let chat_text = app.messages.join("\n");
    
    // Calculate a safe scroll offset so the text doesn't disappear if u16::MAX isn't clamped properly
    let lines_count = chat_text.lines().count();
    let inner_height = mobile_chunks[1].height.saturating_sub(2) as usize;
    let max_scroll = lines_count.saturating_sub(inner_height);
    let scroll_y = max_scroll.saturating_sub(app.scroll) as u16;
    
    let chat_widget = Paragraph::new(chat_text)
        .block(Block::default().borders(Borders::ALL).title(chat_title).style(Style::default().fg(theme_rgb)))
        .style(Style::default().fg(text_rgb))
        .wrap(ratatui::widgets::Wrap { trim: false })
        .scroll((scroll_y, 0));
        
    f.render_widget(chat_widget, mobile_chunks[1]);

    // --- Render Command Deck Input (Bottom) ---
    let input_widget = Paragraph::new(app.input.value()).block(
        Block::default().borders(Borders::ALL).title(" Request Objective (ESC to quit) ").style(Style::default().fg(theme_rgb))
    ).style(Style::default().fg(text_rgb));
    f.render_widget(input_widget, mobile_chunks[2]);

    // --- Render Slash Command Suggestions (Floating) ---
    let matches = app.get_suggestions();
    if !matches.is_empty() {
        let suggest_height = (matches.len() as u16 + 2).min(7);
        let suggest_area = ratatui::layout::Rect {
            x: mobile_chunks[2].x,
            y: mobile_chunks[2].y.saturating_sub(suggest_height),
            width: mobile_chunks[2].width,
            height: suggest_height,
        };
        
        let suggest_items: Vec<ListItem> = matches.iter().enumerate().map(|(i, s)| {
            let mut style = Style::default().fg(Color::Yellow);
            if i == app.suggestion_index % matches.len() {
                style = style.bg(Color::DarkGray).fg(Color::White); // Highlight
            }
            ListItem::new(s.to_string()).style(style)
        }).collect();
        
        let suggest_list = List::new(suggest_items).block(
            Block::default().borders(Borders::ALL).title(" Suggestions (Use Arrows/Tab to apply) ").style(Style::default().fg(theme_rgb))
        );
        
        f.render_widget(ratatui::widgets::Clear, suggest_area);
        f.render_widget(suggest_list, suggest_area);
    }

    // Make the cursor blink dynamically in the input box
    f.set_cursor(
        mobile_chunks[2].x + app.input.visual_cursor() as u16 + 1,
        mobile_chunks[2].y + 1,
    );
}
