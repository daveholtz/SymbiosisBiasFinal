library(ggplot2)
library(dplyr)
library(tidyr)
library(grid)
library(scales)
library(systemfonts)

tur_vs_pct_trt <- read.csv('./results/TU_rates_VS_Percentage_Treatment_final.csv')

tur_vs_pct_trt <- tur_vs_pct_trt %>%
  mutate(algo1 = case_when(algo1 == 'Item' ~ 'Item-based CF',
                           algo1 == 'User' ~ 'User-based CF',
                           algo1 == 'Ideal' ~ 'Oracle',
                           algo1 == 'Random' ~ 'Random'),
         algo2 = case_when(algo2 == 'Item' ~ 'Item-based CF',
                           algo2 == 'User' ~ 'User-based CF',
                           algo2 == 'Ideal' ~ 'Oracle',
                           algo2 == 'Random' ~ 'Random'),
         method = case_when(method == 'Cluster' ~ 'Cluster-randomized',
                            method == 'Naive' ~ 'Naive',
                            method == 'Split' ~ 'Data-diverted',
                            method == 'User-corpus' ~ 'User-corpus co-diverted')) %>%
  mutate(TUR_algo_1 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_1))),
         TUR_algo_2 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_2)))) %>%
  separate(TUR_algo_1, into = c("TUR_algo_1_mean", "TUR_algo_1_lb", "TUR_algo_1_ub"), sep = " ") %>% 
  separate(TUR_algo_2, into = c("TUR_algo_2_mean", "TUR_algo_2_lb", "TUR_algo_2_ub"), sep = " ") %>% 
  mutate(across(c(TUR_algo_1_mean, TUR_algo_2_mean, TUR_algo_1_lb, TUR_algo_2_lb, TUR_algo_1_ub, TUR_algo_2_ub), as.numeric))

reference_lines <- tur_vs_pct_trt %>% 
  filter(algo1 == algo2) %>% head(n=4)

p <- tur_vs_pct_trt %>% 
  filter(algo2 != algo1) %>%
  filter(algo2 %in% c('Item-based CF', 'User-based CF')) %>%
  mutate(treatment_percentage = case_when(method == 'Cluster-randomized' ~ treatment_percentage - .01,
                                          method == 'Data-diverted' ~ treatment_percentage + .01,
                                          method == 'User-corpus co-diverted' ~ treatment_percentage + .02,
                                          TRUE ~ treatment_percentage - .02)) %>%
  mutate(algo2 = factor(algo2, levels = c("Oracle", "Random", "Item-based CF", "User-based CF"), ordered = TRUE)) %>%
  mutate(algo1 = factor(algo1, levels = c("Oracle", "Random", "Item-based CF", "User-based CF"), ordered = TRUE)) %>%
  mutate(hline_mean = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_mean[1],
                                algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_mean[1],
                                algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_mean[1],
                                algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_mean[1],)) %>%
  mutate(hline_lb = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_lb[1],
                              algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_lb[1],
                              algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_lb[1],
                              algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_lb[1],)) %>% 
  mutate(hline_ub = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_ub[1],
                              algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_ub[1],
                              algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_ub[1],
                              algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_ub[1],)) %>% 
  ggplot(., aes(x=treatment_percentage, y=TUR_algo_2_mean, color=method)) + 
  geom_hline(aes(yintercept = hline_mean), color = "black", linetype = "solid") +
  geom_rect(aes(xmin=-Inf, xmax=Inf, ymin=hline_lb, ymax=hline_ub), fill='black', color=NA, alpha=.01) + 
  geom_pointrange(aes(ymin=TUR_algo_2_lb, ymax=TUR_algo_2_ub), size=.15) + facet_grid(algo2~algo1, scales='free_y') + 
  theme_minimal() + 
  theme(
    panel.border = element_rect(colour = "grey", fill = NA, size = 1),  
    plot.margin = margin(25, 25, 25, 25),  
    plot.background = element_rect(colour = "grey", fill = NA, size = 1),
    plot.title = element_text(size = 10),
    axis.title.x = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    legend.title = element_blank(),
    legend.text = element_text(size = 10),
    legend.position = 'bottom'
  ) +
  xlab('Proportion of Users Treated') + 
  ylab('Treatment Algorithm Take-up Rate') +
  scale_x_continuous(lim=c(0,1), labels=percent) + 
  scale_y_continuous(labels=percent)

p

pdf(file = "./plots/trt_pct_plot.pdf", width = 11, height = 6, paper = "special")

grid.newpage()

# Arrange the plot with extra labels using grid
grid.draw(ggplotGrob(p))

# Add facet labels as "external axis labels"
grid.text('Control Algorithm', x = 0.5, y = 0.98, gp = gpar(fontsize = 13))  # Top label
grid.text('Treatment Algorithm', x = 0.98, y = 0.5, rot = -90, gp = gpar(fontsize = 13))  # Left label
dev.off()

tur_vs_gamma_pref <- read.csv('./results/TU_rates_VS_Gamma_Pref_final.csv')

tur_vs_gamma_pref <- tur_vs_gamma_pref %>%
  mutate(algo1 = case_when(algo1 == 'Item' ~ 'Item-based CF',
                           algo1 == 'User' ~ 'User-based CF',
                           algo1 == 'Ideal' ~ 'Oracle',
                           algo1 == 'Random' ~ 'Random'),
         algo2 = case_when(algo2 == 'Item' ~ 'Item-based CF',
                           algo2 == 'User' ~ 'User-based CF',
                           algo2 == 'Ideal' ~ 'Oracle',
                           algo2 == 'Random' ~ 'Random'),
         method = case_when(method == 'Cluster' ~ 'Cluster-randomized',
                            method == 'Naive' ~ 'Naive',
                            method == 'Split' ~ 'Data-diverted',
                            method == 'User-corpus' ~ 'User-corpus co-diverted')) %>%
  mutate(TUR_algo_1 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_1))),
         TUR_algo_2 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_2)))) %>%
  separate(TUR_algo_1, into = c("TUR_algo_1_mean", "TUR_algo_1_lb", "TUR_algo_1_ub"), sep = " ") %>% 
  separate(TUR_algo_2, into = c("TUR_algo_2_mean", "TUR_algo_2_lb", "TUR_algo_2_ub"), sep = " ") %>% 
  mutate(across(c(TUR_algo_1_mean, TUR_algo_2_mean, TUR_algo_1_lb, TUR_algo_2_lb, TUR_algo_1_ub, TUR_algo_2_ub), as.numeric))

reference_points <- tur_vs_gamma_pref %>% filter(algo1 == algo2) %>% dplyr::select(gamma_pref, algo1, TUR_algo_1_mean) %>% 
  rename(reference_tur = TUR_algo_1_mean)

jitter_minus_large = .8
jitter_minus_small = .9
jitter_plus_small = 1.1
jitter_plus_large = 1.2

p2 <- tur_vs_gamma_pref %>% 
  filter(algo2 != algo1) %>%
  filter(algo1 %in% c('Item-based CF', 'User-based CF')) %>%
  mutate(algo2 = factor(algo2, levels = c("Oracle", "Random", "Item-based CF", "User-based CF"), ordered = TRUE)) %>%
  dplyr::left_join(., reference_points) %>%
  mutate(gamma_pref = case_when(method == 'Cluster-randomized' ~ gamma_pref*jitter_minus_small,
                                method == 'Data-diverted' ~ gamma_pref*jitter_plus_small,
                                method == 'User-corpus co-diverted' ~ gamma_pref*jitter_plus_large,
                                TRUE ~ gamma_pref*jitter_minus_large)) %>%
  ggplot(., aes(x=gamma_pref, y=TUR_algo_1_mean - reference_tur, color=method)) + 
  geom_hline(aes(yintercept = 0), color = "black", linetype = "solid") +
  geom_pointrange(aes(ymin=TUR_algo_1_lb - reference_tur, ymax=TUR_algo_1_ub - reference_tur), size=.15) + facet_grid(algo1~algo2, scales='free_y') + 
  theme_minimal() + 
  theme(
    panel.border = element_rect(colour = "grey", fill = NA, size = 1),  
    plot.margin = margin(25, 25, 25, 25),  
    plot.background = element_rect(colour = "grey", fill = NA, size = 1),
    plot.title = element_text(size = 10),
    axis.title.x = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    legend.title = element_blank(),
    legend.text = element_text(size = 10),
    legend.position = 'bottom'
  ) + 
  xlab(expression(gamma[pref])) + 
  ylab('Bias in Treatment Algorithm\nTake-up Rate Estimate') +
  scale_y_continuous(labels=percent) + 
  scale_x_log10()

p2

pdf(file = "./plots/gamma_pref_plot.pdf", width = 11, height = 6)

grid.newpage()

# Arrange the plot with extra labels using grid
grid.draw(ggplotGrob(p2))

# Add facet labels as "external axis labels"
grid.text('Control Algorithm', x = 0.5, y = 0.98, gp = gpar(fontsize = 13))  # Top label
grid.text('Treatment Algorithm', x = 0.98, y = 0.5, rot = -90, gp = gpar(fontsize = 13))  # Left label
dev.off()

bias_plot_data <- read.csv('./results/TU_rates_VS_Gamma_Pref_final.csv')

true_tur <- bias_plot_data %>% 
  mutate(algo1 = case_when(algo1 == 'Item' ~ 'Item-based CF',
                           algo1 == 'User' ~ 'User-based CF',
                           algo1 == 'Ideal' ~ 'Oracle',
                           algo1 == 'Random' ~ 'Random'),
         algo2 = case_when(algo2 == 'Item' ~ 'Item-based CF',
                           algo2 == 'User' ~ 'User-based CF',
                           algo2 == 'Ideal' ~ 'Oracle',
                           algo2 == 'Random' ~ 'Random')) %>%
  filter(method == 'Ref') %>% 
  filter(gamma_pref == 1) %>% 
  mutate(TUR_algo_1 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_1)))) %>%
  separate(TUR_algo_1, into = c("TUR_algo_1_mean", "TUR_algo_1_lb", "TUR_algo_1_ub"), sep = " ") %>% 
  dplyr::select(algo1, TUR_algo_1_mean) %>% 
  head(n=4)

p3 <- bias_plot_data %>% 
  mutate(algo1 = case_when(algo1 == 'Item' ~ 'Item-based CF',
                           algo1 == 'User' ~ 'User-based CF',
                           algo1 == 'Ideal' ~ 'Oracle',
                           algo1 == 'Random' ~ 'Random'),
         algo2 = case_when(algo2 == 'Item' ~ 'Item-based CF',
                           algo2 == 'User' ~ 'User-based CF',
                           algo2 == 'Ideal' ~ 'Oracle',
                           algo2 == 'Random' ~ 'Random'),
         method = case_when(method == 'Cluster' ~ 'Cluster-randomized',
                            method == 'Naive' ~ 'Naive',
                            method == 'Split' ~ 'Data-diverted',
                            method == 'User-corpus' ~ 'User-corpus co-diverted')) %>%
  filter(method != 'Ref') %>% 
  filter(gamma_pref == 10) %>%
  mutate(TE = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TE)))) %>%
  separate(TE, into = c("TE_mean", "TE_lb", "TE_ub", "TE_var"), sep = " ") %>% 
  mutate(TE_mean = as.numeric(TE_mean)) %>%
  filter(algo1 %in% c('Item-based CF', 'User-based CF')) %>%
  left_join(., true_tur, by=c('algo1' = 'algo1')) %>% 
  left_join(., true_tur, by=c('algo2' = 'algo1')) %>% 
  rename(true_tur_algo1 = TUR_algo_1_mean.x,
         true_tur_algo2 = TUR_algo_1_mean.y) %>% 
  mutate(true_te = as.numeric(true_tur_algo1) - as.numeric(true_tur_algo2),
         bias = true_te - TE_mean,
         rmse = sqrt(as.numeric(TE_var)*1000 + bias^2)) %>%
  mutate(algo1 = case_when(algo1 == 'User-based CF' ~ 'Treatment Algorithm = User-based CF',
                           algo1 == 'Item-based CF' ~ 'Treatment Algorithm = Item-based CF')) %>% 
  ggplot(., aes(x=algo2, y=abs(bias), fill=method)) + geom_bar(stat='identity', position='dodge') + facet_wrap(~algo1, scales='free', ncol=1) + 
  theme_minimal() + 
  theme(
    panel.border = element_rect(colour = "grey", fill = NA, size = 1),  
    plot.margin = margin(25, 25, 25, 25),  
    plot.background = element_rect(colour = "grey", fill = NA, size = 1),
    plot.title = element_text(size = 10),
    axis.title.x = element_text(size = 10),
    strip.text.x = element_text(size=11),
    axis.title.y = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    legend.title = element_blank(),
    legend.text = element_text(size = 8),
    legend.position = 'bottom'
  ) + 
  xlab('Control Algorithm') + 
  ylab('Abs. Bias in Treatment Effect Estimate') + 
  guides(fill = guide_legend(nrow = 2))

pdf(file = "./plots/bias_plot.pdf", width = 4, height = 6)

grid.newpage()

# Arrange the plot with extra labels using grid
grid.draw(ggplotGrob(p3))
dev.off()

tur_vs_clus_qual <- read.csv('./results/TU_rates_VS_Cluster_Quality_final.csv')

tur_vs_clus_qual <- tur_vs_clus_qual %>%
  mutate(algo1 = case_when(algo1 == 'Item' ~ 'Item-based CF',
                           algo1 == 'User' ~ 'User-based CF',
                           algo1 == 'Ideal' ~ 'Oracle',
                           algo1 == 'Random' ~ 'Random'),
         algo2 = case_when(algo2 == 'Item' ~ 'Item-based CF',
                           algo2 == 'User' ~ 'User-based CF',
                           algo2 == 'Ideal' ~ 'Oracle',
                           algo2 == 'Random' ~ 'Random'),
         method = case_when(method == 'Cluster' ~ 'Cluster-randomized',
                            method == 'Naive' ~ 'Naive',
                            method == 'Split' ~ 'Data-diverted',
                            method == 'User-corpus' ~ 'User-corpus co-diverted')) %>%
  mutate(TUR_algo_1 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_1))),
         TUR_algo_2 = trimws(gsub("\\s+", " ", gsub("\\[|\\]", "", TUR_algo_2)))) %>%
  separate(TUR_algo_1, into = c("TUR_algo_1_mean", "TUR_algo_1_lb", "TUR_algo_1_ub"), sep = " ") %>% 
  separate(TUR_algo_2, into = c("TUR_algo_2_mean", "TUR_algo_2_lb", "TUR_algo_2_ub"), sep = " ") %>% 
  mutate(across(c(TUR_algo_1_mean, TUR_algo_2_mean, TUR_algo_1_lb, TUR_algo_2_lb, TUR_algo_1_ub, TUR_algo_2_ub), as.numeric))

reference_lines <- tur_vs_clus_qual %>% 
  filter(algo1 == algo2) %>% head(n=4)

p4 <- tur_vs_clus_qual %>% 
  filter(algo2 != algo1) %>%
  filter(algo2 %in% c('Item-based CF', 'User-based CF')) %>%
  mutate(cluster_shuffle_percentage = case_when(method == 'Cluster-randomized' ~ cluster_shuffle_percentage - .01,
                                          method == 'Data-diverted' ~ cluster_shuffle_percentage + .01,
                                          method == 'User-corpus co-diverted' ~ cluster_shuffle_percentage + .02,
                                          TRUE ~ cluster_shuffle_percentage - .02)) %>%
  mutate(algo2 = factor(algo2, levels = c("Oracle", "Random", "Item-based CF", "User-based CF"), ordered = TRUE)) %>%
  mutate(algo1 = factor(algo1, levels = c("Oracle", "Random", "Item-based CF", "User-based CF"), ordered = TRUE)) %>%
  mutate(hline_mean = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_mean[1],
                                algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_mean[1],
                                algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_mean[1],
                                algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_mean[1],)) %>%
  mutate(hline_lb = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_lb[1],
                              algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_lb[1],
                              algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_lb[1],
                              algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_lb[1],)) %>% 
  mutate(hline_ub = case_when(algo2 == 'Item-based CF' ~ filter(reference_lines, algo1=='Item-based CF')$TUR_algo_1_ub[1],
                              algo2 == 'User-based CF' ~ filter(reference_lines, algo1=='User-based CF')$TUR_algo_1_ub[1],
                              algo2 == 'Random' ~ filter(reference_lines, algo1=='Random')$TUR_algo_1_ub[1],
                              algo2 == 'Oracle' ~ filter(reference_lines, algo1=='Oracle')$TUR_algo_1_ub[1],)) %>% 
  ggplot(., aes(x=cluster_shuffle_percentage, y=TUR_algo_2_mean, color=method)) + 
  geom_hline(aes(yintercept = hline_mean), color = "black", linetype = "solid") +
  geom_rect(aes(xmin=-Inf, xmax=Inf, ymin=hline_lb, ymax=hline_ub), fill='black', color=NA, alpha=.01) + 
  geom_pointrange(aes(ymin=TUR_algo_2_lb, ymax=TUR_algo_2_ub), size=.15) + facet_grid(algo2~algo1, scales='free_y') + 
  theme_minimal() + 
  theme(
    panel.border = element_rect(colour = "grey", fill = NA, size = 1),  
    plot.margin = margin(25, 25, 25, 25),  
    plot.background = element_rect(colour = "grey", fill = NA, size = 1),
    plot.title = element_text(size = 10),
    axis.title.x = element_text(size = 10),
    axis.title.y = element_text(size = 10),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    legend.title = element_blank(),
    legend.text = element_text(size = 10),
    legend.position = 'bottom'
  ) +
  xlab('Proportion of Cluster Assignments Reshuffled') + 
  ylab('Treatment Algorithm Take-up Rate') +
  scale_x_continuous(lim=c(-.02,1.02), labels=percent) + 
  scale_y_continuous(labels=percent)

pdf(file = "./plots/cluster_quality_plot.pdf", width = 11, height = 6)

grid.newpage()

# Arrange the plot with extra labels using grid
grid.draw(ggplotGrob(p4))
dev.off()
